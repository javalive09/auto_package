from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xui_package.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'tools.views.home', name='home'),
    url(r'^package/$', 'tools.views.package', name='package'),
    url(r'^admin/', include(admin.site.urls)),
)
