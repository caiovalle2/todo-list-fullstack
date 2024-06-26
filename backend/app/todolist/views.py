from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from todolist.serializers import TaskSerializer
from todolist.models import Task
from datetime import datetime, timedelta
# Create your views here.

class TaskView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        data = self.set_fields(request, data)
        
        serializer = TaskSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response({'message': 'Task cannot be created'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        queryset = Task.objects.filter(assigned_to=request.user) if not self.has_permission(request) else Task.objects.all()
        queryset = queryset.filter(is_active=True)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        task = Task.objects.filter(id=id).first()
        data = request.data
        if task and (task.status != 'done' or not data.get('is_active', True)):
            if task.assigned_to != request.user and not self.has_permission(request):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        task = Task.objects.filter(id=id).first()
        if task:
            if task.assigned_to != request.user and not self.has_permission(request):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def set_fields(self, request, data):
        if not data.get('assigned_to'):
            data['assigned_to'] = request.user.id
        if not data.get('deadline'):
            next_week = datetime.now() + timedelta(weeks=1)
            data['deadline'] = next_week.date()
        
        return data
    
    def has_permission(self, request):
        return request.user.groups.filter(name='admin').exists()