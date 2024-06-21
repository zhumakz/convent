from django.urls import path
from .views import campaign_list, campaign_detail, vote_for_campaign, campaign_voters

urlpatterns = [
    path('', campaign_list, name='campaign_list'),
    path('<int:campaign_id>/', campaign_detail, name='campaign_detail'),
    path('<int:campaign_id>/vote/', vote_for_campaign, name='vote_for_campaign'),
    path('<int:campaign_id>/voters/', campaign_voters, name='campaign_voters'),
]