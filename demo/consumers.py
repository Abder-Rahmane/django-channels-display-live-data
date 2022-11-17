from djangochannelsrestframework import permissions
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer

from .models import Post
from .serializers import PostSerializer


class PostConsumer(ListModelMixin, GenericAsyncAPIConsumer):

    def get_queryset(self, **kwargs):
        return HubriseOrder.objects.filter(ascount=self.scope["user"]).exclude(status__in=['En attente', 'Rejeter', 'Compléter', 'new', 'Livraison échouer']).order_by('created_at')
    serializer_class = PostSerializer
    permissions = (permissions.AllowAny,)

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()

    @model_observer(Post)
    async def model_change(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        return dict(data=PostSerializer(instance=instance).data, action=action.value)
