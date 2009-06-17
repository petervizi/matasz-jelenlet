# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       (r'^$', 'jelenlet.views.index'),
                       (r'^list/(?P<list_from>\d*)$', 'jelenlet.views.list'),
                       (r'^login$', 'jelenlet.views.login'),
                       (r'^logout$', 'jelenlet.views.logout'),
                       (r'^nickchange$', 'jelenlet.views.nickchange'),
                       (r'^user/(?P<name>.+)/', 'jelenlet.views.user'),
                       (r'^week/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})', 'jelenlet.views.week'),
                       (r'^hit$', 'jelenlet.views.hit'),
                       (r'^userno$', 'jelenlet.views.userno'),
                       (r'^base_stats$', 'jelenlet.views.base_stats'),
                       (r'^timestat/(?P<duration>(week)|(month))/(?P<user>.+)/(?P<fyear>\d{4})-(?P<fmonth>\d{2})-(?P<fday>\d{2})', 'jelenlet.views.timestat'),
                       #(r'^activity$', 'jelenlet.views.activity'),
                       (r'^activeusers/(?P<duration>(week)|(month))/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<hfrom>\d{2})-(?P<hto>\d{2})', 'jelenlet.views.activeusers'),
                       (r'^hits/(?P<page>\d*)', 'jelenlet.views.hits'),
    # Example:
    # (r'^foo/', include('foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
