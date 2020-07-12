import csv, io
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .models import Teacher, Subject
from .forms import TeacherForm
from django.forms import modelformset_factory

def home(request):
    teachers = Teacher.objects.all()
    first_name_contains_query = request.GET.get('first_name_contains')
    last_name_contains_query = request.GET.get('last_name_contains')
    subject_query = request.GET.get('subject')

    # Searching any character in the First Name of Teacher
    if first_name_contains_query != '' and first_name_contains_query is not None:
        teachers = Teacher.objects.filter(first_name__icontains=first_name_contains_query)

    # Searching any character in the Last Name of Teacher
    elif last_name_contains_query != '' and last_name_contains_query is not None:
        teachers = Teacher.objects.filter(last_name__icontains=last_name_contains_query)

    # Searching Subject
    elif subject_query != '' and subject_query is not None:
        teachers = Teacher.objects.select_related().filter(subject__subject__icontains=subject_query)

    context = {
        'queryset': teachers,
    }
    return render(request, 'teachers/home.html', context)


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'teachers/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'teachers/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password did not match.'})
        else:
            login(request, user)
            return redirect('currentteachers')


def currentteachers(request):
    teachers = Teacher.objects.all()
    subjects = Subject.objects.all()
    first_name_contains_query = request.GET.get('first_name_contains')
    last_name_contains_query = request.GET.get('last_name_contains')
    subject_query = request.GET.get('subject')

    # Searching any character in the First Name of Teacher
    if first_name_contains_query != '' and first_name_contains_query is not None:
        teachers = Teacher.objects.filter(first_name__icontains=first_name_contains_query)

    # Searching any character in the Last Name of Teacher
    elif last_name_contains_query != '' and last_name_contains_query is not None:
        teachers = Teacher.objects.filter(last_name__icontains=last_name_contains_query)

    # Searching Subject
    elif subject_query != '' and subject_query is not None:
        teachers = Teacher.objects.select_related().filter(subject__subject__icontains=subject_query)

    context = {
        'queryset': teachers,
        'subject_query': subjects
    }
    return render(request, 'teachers/currentteachers.html', context)


def createteacher(request):
    # Formsets for Subjects
    SubjectFormset = modelformset_factory(Subject, fields=('subject',), extra=5)

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        formset = SubjectFormset(request.POST)
        if form.is_valid() and formset.is_valid():

            # Check if email exist
            email = request.POST['email']
            email_exist = Teacher.objects.all().filter(email=email)
            if email_exist:
                return render(request, 'teachers/createteacher.html',
                              {'form': AuthenticationForm(), 'error': 'Email already exist.'})
            else:
                newteacher = form.save(commit=False)
                newteacher.user = request.user
                newteacher.save()

                # Saving Subjects
                for sub in formset:
                    try:
                        subject = Subject(teacher=newteacher, subject=sub.cleaned_data['subject'])
                        subject.save()
                    except Exception as e:
                        break
                return redirect('currentteachers')

    else:
        form = TeacherForm()
        formset = SubjectFormset(queryset=Subject.objects.none())
        context = {
            'form': form,
            'formset': formset,
        }
        return render(request, 'teachers/createteacher.html', context)


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def importteacher(request):
    if request.method == 'GET':
        return render(request, 'teachers/importteacher.html')

    # Importing CSV file
    csv_file = request.FILES['file']

    # File verification
    if not csv_file.name.endswith('.csv'):
        return render(request, 'teachers/importteacher.html',
                      {'form': AuthenticationForm(), 'error': 'The file is not a CSV format'})

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=','):
        _, created = Teacher.objects.update_or_create(
            first_name=column[0],
            last_name=column[1],
            email=column[2],
            phone=column[3],
            room=column[4],
        )
    context = {}
    return render(request, 'teachers/importteacher.html', context)


def viewteacher(request, teacher_pk):
    teacher = get_object_or_404(Teacher, pk=teacher_pk)
    if request.method == 'GET':
        form = TeacherForm(instance=teacher)
        return render(request, 'teachers/viewteacher.html', {'teacher': teacher, 'form': form})
    else:
        try:
            form = TeacherForm(request.POST, instance=teacher)
            form.save()
            return redirect('currentteacher')
        except ValueError:
            return render(request, 'teachers/viewteacher.html', {'teacher': teacher, 'form': form, 'error': 'Bad info'})
