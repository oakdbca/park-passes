from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from org_model_documents.models import Document
from org_model_documents.serializers import DocumentSerializer
from org_model_logs.serializers import (
    CommunicationsLogEntrySerializer,
    UserActionSerializer,
)
from parkpasses.ledger_api_utils import retrieve_email_user


class UserActionSerializer(UserActionSerializer):
    who = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def get_who(self, obj):
        return retrieve_email_user(obj.who).get_full_name()

    def get_documents(self, obj):
        documents = []
        content_type = ContentType.objects.get_for_model(obj)
        if Document.objects.filter(
            content_type=content_type, object_id=obj.id
        ).exists():
            documents = Document.objects.filter(
                content_type=content_type, object_id=obj.id
            )
            documents = DocumentSerializer(documents, many=True).data
        return documents


class CommunicationsLogEntrySerializer(CommunicationsLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    def get_documents(self, obj):
        documents = []
        content_type = ContentType.objects.get_for_model(obj)
        if Document.objects.filter(
            content_type=content_type, object_id=obj.id
        ).exists():
            documents = Document.objects.filter(
                content_type=content_type, object_id=obj.id
            )
            documents = DocumentSerializer(documents, many=True).data
        return documents
