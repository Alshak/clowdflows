from workflows.models import Workflow
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from workflows.serializers import WorkflowSerializer
#from rest_framework import filters

class WorkflowViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows workflows to be viewed or edited.
    """
    serializer_class = WorkflowSerializer
    model = Workflow

    def pre_save(self, workflow):
        workflow.user = self.request.user

    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)