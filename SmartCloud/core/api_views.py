from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from .models import School, Student
from attendance.models import DailyAttendance

# Helper to validate School via X-School-Key header
def get_school_from_request(request):
    api_key = request.headers.get('X-School-Key')
    if not api_key:
        return None
    try:
        return School.objects.get(api_key=api_key, is_active=True)
    except (School.DoesNotExist, ValueError):
        return None


# ==========================================
# 1. AGENT INTEGRATION APIS (DO NOT CHANGE CONTRACT)
# ==========================================

class ReceiveLogsAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        school = get_school_from_request(request)
        if not school:
            return Response({"error": "Invalid or missing X-School-Key header"}, status=status.HTTP_401_UNAUTHORIZED)

        # Update last activity timestamp
        school.last_activity = timezone.now()
        school.save()

        logs = request.data.get('logs', [])
        saved = 0

        for log in logs:
            hik_id = log.get('id')
            time_str = log.get('time')
            if not hik_id:
                continue

            try:
                dt = datetime.fromisoformat(time_str)

                student = Student.objects.filter(school=school, hikvision_id=hik_id).first()
                if not student:
                    continue

                obj, created = DailyAttendance.objects.get_or_create(
                    student=student,
                    date=dt.date()
                )

                if created:
                    obj.arrived_at = dt.time()
                    obj.save()
                    saved += 1
                else:
                    if obj.arrived_at and dt.time() > obj.arrived_at:
                        obj.left_at = dt.time()
                        obj.save()
            except Exception as e:
                print(f"Log Error: {e}")

        return Response({"status": "ok", "saved": saved})


class GetNewUsersAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        school = get_school_from_request(request)
        if not school:
            return Response({"error": "Invalid or missing X-School-Key header"}, status=status.HTTP_401_UNAUTHORIZED)

        school.last_activity = timezone.now()
        school.save()

        students = Student.objects.filter(school=school, is_synced=False)[:20]

        data = []
        for u in students:
            photo_url = request.build_absolute_uri(u.photo.url) if u.photo else None
            data.append({
                "db_id": u.id,
                "type": "student",
                "full_name": u.full_name,
                "hikvision_id": u.hikvision_id,
                "photo_url": photo_url
            })

        return Response({"users": data})


class ConfirmUserSyncAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        school = get_school_from_request(request)
        if not school:
            return Response({"error": "Invalid or missing X-School-Key header"}, status=status.HTTP_401_UNAUTHORIZED)

        synced_hik_ids = request.data.get('synced_ids', [])
        if synced_hik_ids:
            Student.objects.filter(school=school, hikvision_id__in=synced_hik_ids).update(is_synced=True)
            print(f"✅ Sync confirmed for IDs: {synced_hik_ids}")

        return Response({"status": "ok"})


# ==========================================
# 2. STUDENT & ATTENDANCE REST APIS
# ==========================================

class StudentListCreateAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        school = get_school_from_request(request)
        if not school:
            return Response({"error": "Invalid or missing X-School-Key header"}, status=status.HTTP_401_UNAUTHORIZED)

        students = Student.objects.filter(school=school).order_by('-id')
        data = []
        for s in students:
            photo_url = request.build_absolute_uri(s.photo.url) if s.photo else None
            data.append({
                "id": s.id,
                "full_name": s.full_name,
                "hikvision_id": s.hikvision_id,
                "photo_url": photo_url,
                "is_synced": s.is_synced
            })

        return Response({"count": len(data), "students": data})

    def post(self, request):
        school = get_school_from_request(request)
        if not school:
            return Response({"error": "Invalid or missing X-School-Key header"}, status=status.HTTP_401_UNAUTHORIZED)

        full_name = request.data.get('full_name')
        photo = request.FILES.get('photo') or request.data.get('photo')

        if not full_name:
            return Response({"error": "full_name field is required"}, status=status.HTTP_400_BAD_REQUEST)

        student = Student(
            school=school,
            full_name=full_name,
            photo=photo,
            is_synced=False
        )
        student.save()

        photo_url = request.build_absolute_uri(student.photo.url) if student.photo else None

        return Response({
            "message": "Student created successfully",
            "student": {
                "id": student.id,
                "full_name": student.full_name,
                "hikvision_id": student.hikvision_id,
                "photo_url": photo_url,
                "is_synced": student.is_synced
            }
        }, status=status.HTTP_201_CREATED)


class AttendanceListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        school = get_school_from_request(request)
        if not school:
            return Response({"error": "Invalid or missing X-School-Key header"}, status=status.HTTP_401_UNAUTHORIZED)

        target_date_str = request.GET.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = date.today()

        records = DailyAttendance.objects.filter(student__school=school, date=target_date).select_related('student')

        data = []
        for r in records:
            data.append({
                "student_id": r.student.id,
                "student_name": r.student.full_name,
                "hikvision_id": r.student.hikvision_id,
                "date": str(r.date),
                "arrived_at": str(r.arrived_at) if r.arrived_at else None,
                "left_at": str(r.left_at) if r.left_at else None,
            })

        return Response({"date": str(target_date), "count": len(data), "attendance": data})