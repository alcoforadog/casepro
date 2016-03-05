from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import CaseCRUDL, PartnerCRUDL
from .views import InboxView, FlaggedView, OpenCasesView, ClosedCasesView, ArchivedView, UnlabelledView
from .views import StatusView, PingView


urlpatterns = CaseCRUDL().as_urlpatterns()
urlpatterns += PartnerCRUDL().as_urlpatterns()

urlpatterns += [
    url(r'^$', InboxView.as_view(), name='cases.inbox'),
    url(r'^flagged/$', FlaggedView.as_view(), name='cases.flagged'),
    url(r'^archived/$', ArchivedView.as_view(), name='cases.archived'),
    url(r'^unlabelled/$', UnlabelledView.as_view(), name='cases.unlabelled'),
    url(r'^open/$', OpenCasesView.as_view(), name='cases.open'),
    url(r'^closed/$', ClosedCasesView.as_view(), name='cases.closed'),
    url(r'^status$', StatusView.as_view(), name='internal.status'),
    url(r'^ping$', PingView.as_view(), name='internal.ping')
]
