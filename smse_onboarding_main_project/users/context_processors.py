from .models import Faculty

def faculty_processor(request):
    """
    Context processor that adds faculty information to the template context.
    """
    if not request.user.is_authenticated:
        return {'faculty': None}
    
    try:
        faculty = Faculty.objects.get(user=request.user)
        return {'faculty': faculty}
    except Faculty.DoesNotExist:
        return {'faculty': None} 
