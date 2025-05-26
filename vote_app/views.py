from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count
from .models import Poll, Option, Vote, User
from .forms import RegisterForm, LoginForm, PollForm, OptionForm

# --- Helpers ---

def is_admin(user):
    return user.is_authenticated and user.is_admin

# --- Auth ---


@login_required
def results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    options = poll.options.annotate(votes_count=Count('vote')).order_by('-votes_count')
    total_votes = Vote.objects.filter(poll=poll).count()

    # Récupère les votes de l'utilisateur pour ce sondage
    try:
        user_vote = Vote.objects.get(poll=poll, user=request.user)
        # accède aux options choisies via ManyToMany
        user_selected_options = [opt.name for opt in user_vote.options.all()]
    except Vote.DoesNotExist:
        user_selected_options = []

    return render(request, 'vote_app/results.html', {
        'poll': poll,
        'options': options,
        'total_votes': total_votes,
        'user_selected_options': user_selected_options,
    })

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            return redirect('poll_list')  # <-- cette ligne redirige vers 'poll_list'
    else:
        form = RegisterForm()
    return render(request, 'vote_app/register.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('poll_list')
    else:
        form = LoginForm()
    return render(request, 'vote_app/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# --- Polls ---

@login_required
def poll_list(request):
    polls = Poll.objects.all().order_by('-start_date')
    return render(request, 'vote_app/poll_list.html', {'polls': polls})

@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    user_vote = Vote.objects.filter(user=request.user, poll=poll).first()
    return render(request, 'vote_app/poll_detail.html', {'poll': poll, 'user_vote': user_vote})

@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.is_active():
        return render(request, 'vote_app/not_active.html', {'poll': poll})

    if Vote.objects.filter(user=request.user, poll=poll).exists():
        return render(request, 'vote_app/already_voted.html', {'poll': poll})

    if request.method == 'POST':
        selected_options = request.POST.getlist('options')

        if poll.vote_type in ['unique', 'choix_unique'] and len(selected_options) != 1:
            return render(request, 'vote_app/vote.html', {
                'poll': poll,
                'error': "Vous devez sélectionner une seule option."
            })

        vote = Vote.objects.create(user=request.user, poll=poll)
        vote.options.set(Option.objects.filter(id__in=selected_options))
        vote.save()

        return redirect('results', poll_id=poll.id)

    return render(request, 'vote_app/vote.html', {'poll': poll})
def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)

    # Récupérer toutes les options du sondage
    options = poll.options.all()

    # Nombre total de votes (combien d'utilisateurs ont voté pour ce sondage)
    total_votes = Vote.objects.filter(poll=poll).count()

    # Compter combien de votes chaque option a
    # On récupère la liste des options avec le nombre de fois où elles ont été choisies dans les votes
    votes_counts = []
    for option in options:
        count = Vote.objects.filter(poll=poll, options=option).count()
        votes_counts.append(count)

    # Calculer le pourcentage de votes pour chaque option
    options_percentages = []
    for option, count in zip(options, votes_counts):
        percentage = 0
        if total_votes > 0:
            percentage = round((count / total_votes) * 100, 2)
        options_percentages.append({
            'name': option.name,
            'percentage': percentage
        })

    # Préparer les données pour le graphique
    option_names = [opt.name for opt in options]

    context = {
        'poll': poll,
        'total_votes': total_votes,
        'option_names_json': option_names,
        'votes_counts_json': votes_counts,
        'options_percentages': options_percentages,
    }
    return render(request, 'vote_app/results.html', context)
# --- Admin section ---

@user_passes_test(is_admin)
def admin_poll_create(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_poll_list')
    else:
        form = PollForm()
    return render(request, 'vote_app/admin_poll_form.html', {'form': form})

@user_passes_test(is_admin)
def admin_poll_list(request):
    polls = Poll.objects.all().order_by('-start_date')
    return render(request, 'vote_app/admin_poll_list.html', {'polls': polls})

@user_passes_test(is_admin)
def admin_poll_edit(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.method == 'POST':
        form = PollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            return redirect('admin_poll_list')
    else:
        form = PollForm(instance=poll)
    return render(request, 'vote_app/admin_poll_form.html', {'form': form})

@user_passes_test(is_admin)
def admin_poll_delete(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    poll.delete()
    return redirect('admin_poll_list')

@user_passes_test(is_admin)
def admin_option_create(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if poll.has_started():
        return render(request, 'vote_app/error.html', {'message': "Impossible d'ajouter des options, le scrutin a déjà commencé."})
    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.poll = poll
            option.save()
            return redirect('admin_poll_edit', poll_id=poll.id)
    else:
        form = OptionForm()
    return render(request, 'vote_app/admin_option_form.html', {'form': form, 'poll': poll})

@user_passes_test(is_admin)
def admin_option_delete(request, poll_id, option_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if poll.has_started():
        return render(request, 'vote_app/error.html', {'message': "Impossible de supprimer des options, le scrutin a déjà commencé."})
    option = get_object_or_404(Option, id=option_id, poll=poll)
    option.delete()
    return redirect('admin_poll_edit', poll_id=poll.id)

@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'vote_app/admin_user_list.html', {'users': users})

@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_user_list')
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
