from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
#    urlpatterns=patterns('hotkw.kw.views',
#                url(r'^$','index'),
#                url(r'^kw/',include('hotkw.kw.urls')),   
#                ),
    # Examples:
#     url(r'^search/(?P<qs>\w+)/$', 'hotkw.kw.views.getPic'),
     url(r'^neihan$', 'shantie.views.zhongzi'),
     url(r'^save/(?P<url>.+)', 'shantie.views.save_html'),
     url(r'^$', 'shantie.views.mainpage'),


     url(r'^kds$', 'shantie.views.xkds_mainpage'),
     url(r'^kds/post/(?P<post_url>\w+)', 'shantie.views.get_kds_post'),
     url(r'^kds/(?P<page>\d+)', 'shantie.views.xkds'),
     url(r'^kds/manage/(?P<page>\d+)', 'shantie.views.kds_backend'),
     url(r'^kds/remove$', 'shantie.views.remove_kds_post'),
     url(r'^kds/amount', 'shantie.views.get_kds_post_total_amount'),

     url(r'^tieba/post/(?P<post_url>\w+)', 'shantie.views.get_tieba_post'),
     url(r'^tieba/amount', 'shantie.views.get_tieba_post_total_amount'),
     url(r'^tieba/(?P<page>\d+)', 'shantie.views.diba'),
     url(r'^tieba/manage/(?P<page>\d+)', 'shantie.views.tieba_backend'),
     url(r'^tieba/remove$', 'shantie.views.remove_tieba_post'),
     url(r'^tieba/hot/(?P<page>\d+)', 'shantie.views.tieba_today_hot'),


     url(r'^search/(?P<keyword>\w+)/(?P<page>\d+)', 'shantie.views.search_post'),
     url(r'^admin', 'shantie.views.manage_login'),
     url(r'^advice', 'shantie.views.advice_board'),
#    
    # url(r'^hotkw/', include('hotkw.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()  
