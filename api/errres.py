from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

def errres(errMsg, status): 
    response = Response({'error': errMsg }, status=status)
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    
    return response