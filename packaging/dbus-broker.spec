%global c_dvar_version 1
%global c_list_version 3
%global c_rbtree_version 3
%global c_sundry_commit 3b5f04b5af54dea68d832546833d6d460d03aefc

Name:           dbus-broker
Version:        3
Release:        1%{?dist}
Summary:        Linux D-Bus Message Broker
License:        ASL 2.0
URL:            https://github.com/bus1/dbus-broker
Source0:        https://github.com/bus1/dbus-broker/archive/v%{version}/dbus-broker-%{version}.tar.gz
Source1:        https://github.com/c-util/c-dvar/archive/v%{c_dvar_version}/c-dvar-%{c_dvar_version}.tar.gz
Source2:        https://github.com/c-util/c-list/archive/v%{c_list_version}/c-list-%{c_list_version}.tar.gz
Source3:        https://github.com/c-util/c-rbtree/archive/v%{c_rbtree_version}/c-rbtree-%{c_rbtree_version}.tar.gz
Source4:        https://github.com/c-util/c-sundry/archive/%{c_sundry_commit}/c-sundry-%{c_sundry_commit}.tar.gz
Provides:       bundled(c-dvar) = %{c_dvar_version}
Provides:       bundled(c-list) = %{c_list_version}
Provides:       bundled(c-rbtree) = %{c_rbtree_version}
%{?systemd_requires}
BuildRequires:  expat-devel
BuildRequires:  gcc
BuildRequires:  glib2-devel
BuildRequires:  glibc-devel
BuildRequires:  libselinux-devel
BuildRequires:  meson
BuildRequires:  systemd
BuildRequires:  systemd-devel
BuildRequires:  python2-docutils
BuildRequires:  checkpolicy, selinux-policy-devel
Requires:       dbus

%description
Linux D-Bus Message Broker

dbus-broker is an implementation of a message bus as defined by the D-Bus
specification. Its aim is to provide high performance and reliability, while
keeping compatibility to the D-Bus reference implementation. It is exclusively
written for Linux systems, and makes use of many modern features provided by
recent Linux kernel releases.

%prep
%autosetup
%setup -q -T -D -b 1
%setup -q -T -D -b 2
%setup -q -T -D -b 3
%setup -q -T -D -b 4
cd subprojects
rm * -r
ln -s ../../c-dvar-%{c_dvar_version} c-dvar
ln -s ../../c-list-%{c_list_version} c-list
ln -s ../../c-rbtree-%{c_rbtree_version} c-rbtree
ln -s ../../c-sundry-%{c_sundry_commit} c-sundry
cd -
rm -rf %{_vpath_builddir}/docs
mkdir -p %{_vpath_builddir}/docs
rm -rf %{_vpath_builddir}/selinux
mkdir -p %{_vpath_builddir}/selinux
cp %{_vpath_srcdir}/selinux/dbus-broker.{te,fc} %{_vpath_builddir}/selinux/

%build
echo %{_vpath_builddir}
meson --prefix=/usr --buildtype=release %{_vpath_srcdir} %{_vpath_builddir}
%meson_build
rst2man %{_vpath_srcdir}/docs/dbus-broker-launch.rst %{_vpath_builddir}/docs/dbus-broker-launch.1
rst2man %{_vpath_srcdir}/docs/dbus-broker.rst %{_vpath_builddir}/docs/dbus-broker.1
cd %{_vpath_builddir}/selinux
make NAME=targeted -f /usr/share/selinux/devel/Makefile
cd -

%install
%meson_install
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 %{_vpath_builddir}/docs/dbus-broker-launch.1 %{buildroot}%{_mandir}/man1/dbus-broker-launch.1
install -p -m 644 %{_vpath_builddir}/docs/dbus-broker.1 %{buildroot}%{_mandir}/man1/dbus-broker.1
install -d %{buildroot}%{_datadir}/selinux/targeted
install -p -m 644 %{_vpath_builddir}/selinux/dbus-broker.pp %{buildroot}%{_datadir}/selinux/targeted/dbus-broker.pp

%post
/usr/sbin/semodule -s targeted -i %{_datadir}/selinux/targeted/dbus-broker.pp
/sbin/fixfiles -R dbus-broker restore
%systemd_post dbus-broker.service

%preun
%systemd_preun dbus-broker.service

%postun
%systemd_postun dbus-broker.service
if [ $1 -eq 0 ] ; then
  /usr/sbin/semodule -s targeted -r dbus-broker
fi

%files
%license COPYING
%license LICENSE
%{_bindir}/dbus-broker
%{_bindir}/dbus-broker-launch
%{_datadir}/selinux/*/dbus-broker.pp
%{_mandir}/man1/dbus-broker.1*
%{_mandir}/man1/dbus-broker-launch.1*
%{_unitdir}/dbus-broker.service
%{_userunitdir}/dbus-broker.service

%changelog
* Fri Aug 18 2017 Tom Gundersen <teg@jklm.no> - 3-1
- Add manpages

* Wed Aug 16 2017 Tom Gundersen <teg@jklm.no> - 2-2
- Add license to package

* Wed Aug 16 2017 Tom Gundersen <teg@jklm.no> - 2-1
- Add SELinux support

* Sun Aug 13 2017 Tom Gundersen <teg@jklm.no> - 1-1
- Initial RPM release

