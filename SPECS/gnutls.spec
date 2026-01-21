%global package_speccommit 3f9f8b250422d086e1f6c64730d20febb179107e
%global usver 3.3.29
%global xsver 10
%global xsrel %{xsver}%{?xscount}%{?xshash}

%bcond_with dane
%bcond_with guile
Summary: A TLS protocol implementation
Name: gnutls
Version: 3.3.29
Release: %{?xsrel}%{?dist}
# The libraries are LGPLv2.1+, utilities are GPLv3+
License: GPLv3+ and LGPLv2+
Group: System Environment/Libraries
BuildRequires: p11-kit-devel >= 0.23.1, gettext
BuildRequires: zlib-devel, readline-devel, libtasn1-devel >= 3.8
BuildRequires: libtool, automake, autoconf, texinfo
BuildRequires: autogen-libopts-devel >= 5.18 autogen gettext-devel
BuildRequires: nettle-devel >= 2.7.1
BuildRequires: trousers-devel >= 0.3.11.2
BuildRequires: libidn-devel
BuildRequires: gperf
BuildRequires: fipscheck
BuildRequires: softhsm, net-tools
Requires: p11-kit-trust
# The automatic dependency on libtasn1 and p11-kit is insufficient,
Requires: libtasn1 >= 3.9
Requires: p11-kit >= 0.23.1
Requires: trousers >= 0.3.11.2
%if %{with dane}
BuildRequires: unbound-devel unbound-libs
%endif
%if %{with guile}
BuildRequires: guile-devel
%endif
URL: http://www.gnutls.org/
Source0: gnutls-3.3.29-hobbled.tar.xz
Source1: libgnutls-config
Source2: hobble-gnutls
Patch0: gnutls-3.2.7-rpath.patch
Patch1: gnutls-3.1.11-nosrp.patch
Patch2: gnutls-3.3.8-fips-key.patch
Patch3: gnutls-3.3.8-padlock-disable.patch
Patch4: gnutls-3.3.22-eapp-data.patch
Patch5: gnutls-3.3.26-dh-params-1024.patch
Patch6: gnutls-3.3.29-serv-sni-hostname.patch
Patch7: gnutls-3.3.29-serv-unrec-name.patch
Patch8: gnutls-3.3.29-cli-sni-hostname.patch
Patch9: gnutls-3.3.29-tests-sni-hostname.patch
Patch10: gnutls-3.3.29-pkcs11-retrieve-pin-from-uri-once.patch
Patch11: gnutls-3.3.29-dummy-wait-account-len-field.patch
Patch12: gnutls-3.3.29-dummy-wait-hash-same-amount-of-blocks.patch
Patch13: gnutls-3.3.29-cbc-mac-verify-ssl3-min-pad.patch
Patch14: gnutls-3.3.29-remove-hmac-sha384-sha256-from-default.patch
Patch15: gnutls-3.3.29-do-not-run-sni-hostname-windows.patch
Patch16: gnutls-3.3.29-testpkcs11.patch
Patch17: gnutls-3.3.29-disable-failing-tests.patch
Patch18: gnutls-3.3.29-do-not-mark-object-as-private.patch
Patch19: gnutls-3.3.29-re-enable-check-cert-write.patch
Patch20: gnutls-3.3.29-tests-pkcs11-increase-RSA-gen-size.patch
Patch21: gnutls-3.3.29-serv-large-key-resumption.patch
Patch22: gnutls-3.3.29-bring-back-hmac-sha256.patch
Patch23: gnutls-3.3.29-fips140-fix-ecdsa-kat-selftest.patch
Patch24: 0001-CP-50333-Regenerate-expired-test-certificates.patch
Patch25: 0001-CP-50333-Skip-certficate-chain-export-test.patch

# Wildcard bundling exception https://fedorahosted.org/fpc/ticket/174
Provides: bundled(gnulib) = 20130424

%package c++
Summary: The C++ interface to GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}

%package devel
Summary: Development files for the %{name} package
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-c++%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif
Requires: pkgconfig
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%package utils
License: GPLv3+
Summary: Command line tools for TLS protocol
Group: Applications/System
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif

%if %{with dane}
%package dane
Summary: A DANE protocol implementation for GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}
%endif

%if %{with guile}
%package guile
Summary: Guile bindings for the GNUTLS library
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: guile
%endif

%description
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.

%description c++
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.
This package contains the C++ interface for the GnuTLS library.

%description devel
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.
This package contains files needed for developing applications with
the GnuTLS library.

%description utils
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.
This package contains command line TLS client and server and certificate
manipulation tools.

%if %{with dane}
%description dane
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.
This package contains library that implements the DANE protocol for verifying
TLS certificates through DNSSEC.
%endif

%if %{with guile}
%description guile
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.
This package contains Guile bindings for the library.
%endif

%prep
%autosetup -p1

sed 's/gnutls_srp.c//g' -i lib/Makefile.in
sed 's/gnutls_srp.lo//g' -i lib/Makefile.in
rm -f lib/minitasn1/*.c lib/minitasn1/*.h
rm -f src/libopts/*.c src/libopts/*.h src/libopts/compat/*.c src/libopts/compat/*.h

# Touch man pages to avoid them to be regenerated after patches which change
# .def files
touch doc/manpages/gnutls-serv.1
touch doc/manpages/gnutls-cli.1

# Fix permissions for files brought by patches
chmod ugo+x %{_builddir}/%{name}-%{version}/tests/testpkcs11.sh
chmod ugo+x %{_builddir}/%{name}-%{version}/tests/sni-hostname.sh

%{SOURCE2} -e
autoreconf -if

%build
export LDFLAGS="-Wl,--no-add-needed"

%configure --with-libtasn1-prefix=%{_prefix} \
	   --with-default-trust-store-pkcs11="pkcs11:model=p11-kit-trust;manufacturer=PKCS%2311%20Kit" \
           --with-included-libcfg \
	   --with-arcfour128 \
	   --with-ssl3 \
           --disable-static \
           --disable-openssl-compatibility \
           --disable-srp-authentication \
	   --disable-non-suiteb-curves \
	   --with-trousers-lib=%{_libdir}/libtspi.so.1 \
	   --enable-fips140-mode \
%if %{with guile}
           --enable-guile \
%ifarch %{arm}
           --disable-largefile \
%endif
%else
           --disable-guile \
%endif
%if %{with dane}
	   --with-unbound-root-key-file=/var/lib/unbound/root.key \
           --enable-dane \
%else
           --disable-dane \
%endif
           --disable-rpath
# Note that the arm hack above is not quite right and the proper thing would
# be to compile guile with largefile support.
make %{?_smp_mflags}

%define __spec_install_post \
	%{?__debug_package:%{__debug_install_post}} \
	%{__arch_install_post} \
	%{__os_install_post} \
	fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.28.*.* \
	file=`basename $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.28.*.hmac` && mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.libgnutls.so.28.hmac \
%{nil}

%install
make install DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_bindir}/srptool
rm -f $RPM_BUILD_ROOT%{_bindir}/gnutls-srpcrypt
cp -f %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/libgnutls-config
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/srptool.1
rm -f $RPM_BUILD_ROOT%{_mandir}/man3/*srp*
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libguile*.a
%if %{without dane}
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/gnutls-dane.pc
rm -f $RPM_BUILD_ROOT%{_libdir}/libgnutls-dane.so*
rm -f $RPM_BUILD_ROOT%{_bindir}/danetool
%endif

%find_lang gnutls

%check
make check %{?_smp_mflags}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post c++ -p /sbin/ldconfig

%postun c++ -p /sbin/ldconfig

%post devel
if [ -f %{_infodir}/gnutls.info.gz ]; then
    /sbin/install-info %{_infodir}/gnutls.info.gz %{_infodir}/dir || :
fi

%preun devel
if [ $1 = 0 -a -f %{_infodir}/gnutls.info.gz ]; then
   /sbin/install-info --delete %{_infodir}/gnutls.info.gz %{_infodir}/dir || :
fi

%if %{with dane}
%post dane -p /sbin/ldconfig

%postun dane -p /sbin/ldconfig
%endif

%if %{with guile}
%post guile -p /sbin/ldconfig

%postun guile -p /sbin/ldconfig
%endif

%files -f gnutls.lang
%defattr(-,root,root,-)
%{_libdir}/libgnutls.so.28*
%{_libdir}/.libgnutls.so.28*.hmac
%doc COPYING COPYING.LESSER README AUTHORS NEWS THANKS

%files c++
%{_libdir}/libgnutlsxx.so.*

%files devel
%defattr(-,root,root,-)
%{_bindir}/libgnutls*-config
%{_includedir}/*
%{_libdir}/libgnutls*.so
%{_libdir}/.libgnutls.so.*.hmac
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*
%{_infodir}/gnutls*
%{_infodir}/pkcs11-vision*

%files utils
%defattr(-,root,root,-)
%{_bindir}/certtool
%{_bindir}/tpmtool
%{_bindir}/ocsptool
%{_bindir}/psktool
%{_bindir}/p11tool
%{_bindir}/crywrap
%if %{with dane}
%{_bindir}/danetool
%endif
%{_bindir}/gnutls*
%{_mandir}/man1/*
%doc doc/certtool.cfg

%if %{with dane}
%files dane
%defattr(-,root,root,-)
%{_libdir}/libgnutls-dane.so.*
%endif

%if %{with guile}
%files guile
%defattr(-,root,root,-)
%{_libdir}/libguile*.so*
%{_datadir}/guile/site/gnutls
%{_datadir}/guile/site/gnutls.scm
%endif

%changelog
* Mon Oct 21 2024 Deli Zhang <deli.zhang@citrix.com> - 3.3.29-10
- First imported release

