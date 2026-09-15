from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Student


# ==========================================
# O'QUVCHILAR WEB SAHIFALARI
# (Login, Maktab, Rayono filtrsiz)
# ==========================================

def student_list(request):
    query = request.GET.get('q', '')
    students = Student.objects.all().order_by('full_name')

    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(hikvision_id__icontains=query)
        )

    return render(request, 'core/student_list.html', {
        'students': students,
        'query': query,
        'total_count': Student.objects.count(),
        'synced_count': Student.objects.filter(is_synced=True).count(),
        'pending_count': Student.objects.filter(is_synced=False).count(),
    })


def student_create(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        photo = request.FILES.get('photo')
        if full_name:
            # School kerak — birinchi mavjud maktabni olamiz
            from .models import School
            school = School.objects.filter(is_active=True).first()
            if not school:
                messages.error(request, "Avval admin paneldan maktab yarating: /admin/core/school/")
                return redirect('student_list')

            student = Student(
                school=school,
                full_name=full_name,
                photo=photo,
                is_synced=False
            )
            student.save()
            messages.success(request, f"✅ {student.full_name} qo'shildi! Terminal ID: {student.hikvision_id}")
            return redirect('student_list')
        else:
            messages.error(request, "Ism kiritish majburiy!")

    return render(request, 'core/student_form.html', {
        'title': "Yangi O'quvchi Qo'shish"
    })


def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        photo = request.FILES.get('photo')
        if full_name:
            student.full_name = full_name
            if photo:
                student.photo = photo
                student.is_synced = False
            student.save()
            messages.success(request, f"✅ {student.full_name} yangilandi!")
            return redirect('student_list')
        else:
            messages.error(request, "Ism kiritish majburiy!")

    return render(request, 'core/student_form.html', {
        'title': "O'quvchini Tahrirlash",
        'student': student
    })


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.warning(request, f"🗑️ {name} o'chirildi.")
        return redirect('student_list')

    return render(request, 'core/student_delete.html', {'student': student})
