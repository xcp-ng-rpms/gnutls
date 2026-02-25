%global package_speccommit 29274ee556d24bb1ea800cda086d786099c9fe72
%global usver 3.8.8
%global xsver 3
%global xsrel %{xsver}%{?xscount}%{?xshash}

Version: 3.8.8
Release: %{?xsrel}%{?dist}

%bcond_with cxx
%bcond_with bootstrap
%bcond_with dane
%bcond_without fips
%bcond_without gost
%bcond_with certificate_compression
%bcond_with liboqs
%bcond_without tests
%bcond_with srp

%if 0%{?xenserver} < 9
# Disable ktls as XS8 kernel does not support it yet
%bcond_with ktls
%bcond_with crypto_policies
# XS8 gcc is not new enough, use devtoolset instead
%bcond_without devtoolset
%else
%bcond_without ktls
%bcond_without crypto_policies
%bcond_with devtoolset
%endif

Summary: A TLS protocol implementation
Name: gnutls
# The libraries are LGPLv2.1+, utilities are GPLv3+
License: GPL-3.0-or-later AND LGPL-2.1-or-later
BuildRequires: p11-kit-devel >= 0.21.3, gettext-devel
BuildRequires: readline-devel, libtasn1-devel >= 4.3
%if %{with certificate_compression}
BuildRequires: zlib-devel, brotli-devel, libzstd-devel
%endif
%if %{with liboqs}
BuildRequires: liboqs-devel
%endif
%if %{with bootstrap}
BuildRequires: automake, autoconf, gperf, libtool, texinfo
%endif
BuildRequires: nettle-devel >= 3.5.1

BuildRequires: libunistring-devel
BuildRequires: libidn2-devel
%if %{with devtoolset}
BuildRequires: devtoolset-11-gcc, devtoolset-11-gcc-c++
%else
BuildRequires: gcc, gcc-c++
%endif
BuildRequires: git-core

# for a sanity check on cert loading
BuildRequires: p11-kit-trust, ca-certificates
%if %{with crypto_policies}
Requires: crypto-policies
%endif
Requires: p11-kit-trust
%if %{with cxx}
BuildRequires: gcc-c++
%endif
Requires: libtasn1 >= 4.3
Requires: nettle >= 3.4.1

%if %{with dane}
BuildRequires: unbound-devel unbound-libs
%endif
BuildRequires: make

URL: http://www.gnutls.org/
%define short_version %(echo %{version} | grep -m1 -o "[0-9]*\.[0-9]*" | head -1)
Source0: gnutls-3.8.8.tar.xz
Source1: config
Patch0: gnutls-3.2.7-rpath.patch
Patch1: gnutls-3.8.8-tests-ktls-skip-tls12-chachapoly.patch

# Wildcard bundling exception https://fedorahosted.org/fpc/ticket/174
Provides: bundled(gnulib) = 20130424

%if %{with cxx}
%package c++
Summary: The C++ interface to GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}
%endif

%package devel
Summary: Development files for the %{name} package
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with cxx}
Requires: %{name}-c++%{?_isa} = %{version}-%{release}
%endif
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%else
# Remove previous installed version, to avoid "Failed dependencies" on update
Obsoletes: gnutls-dane < %{version}-%{release}
%endif
Requires: pkgconfig

%package utils
License: GPL-3.0-or-later
Summary: Command line tools for TLS protocol
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%else
Obsoletes: gnutls-dane < %{version}-%{release}
%endif

%if %{with dane}
%package dane
Summary: A DANE protocol implementation for GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}
%endif

%description
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.

%if %{with cxx}
%description c++
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and
other required structures.
This package contains the C++ interface for the GnuTLS library.
%endif

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


%prep
%autosetup -p1 -S git

%build

%if %{with devtoolset}
source /opt/rh/devtoolset-11/enable
%endif

%if %{with bootstrap}
# autoconfg try to call gtkdocsize which is not necessary in this case (and not installed)
# workaround the issue by exporting GTKDOCIZE=echo
# https://github.com/spack/spack/issues/23964
export GTKDOCIZE=echo
autoreconf -fi
%endif

sed -i -e 's|sys_lib_dlsearch_path_spec="/lib /usr/lib|sys_lib_dlsearch_path_spec="/lib /usr/lib %{_libdir}|g' configure
rm -f lib/minitasn1/*.c lib/minitasn1/*.h

echo "SYSTEM=NORMAL" >> tests/system.prio

CCASFLAGS="$CCASFLAGS -Wa,--generate-missing-build-notes=yes"
export CCASFLAGS

%if %{with fips}
eval $(sed -n 's/^\(\(NAME\|VERSION_ID\)=.*\)/OS_\1/p' /etc/os-release)
export FIPS_MODULE_NAME="$OS_NAME ${OS_VERSION_ID%%.*} %name"
%endif

mkdir native_build
pushd native_build
%global _configure ../configure
%configure \
%if %{with fips}
           --enable-fips140-mode \
           --with-fips140-module-name="$FIPS_MODULE_NAME" \
           --with-fips140-module-version=%{version}-%{srpmhash} \
%endif
%if %{with gost}
    	   --enable-gost \
%else
	   --disable-gost \
%endif
%if %{with srp}
           --enable-srp-authentication \
%endif
	   --enable-sha1-support \
           --disable-static \
           --disable-openssl-compatibility \
           --disable-non-suiteb-curves \
%if %{with crypto_policies}
           --with-system-priority-file=%{_sysconfdir}/crypto-policies/back-ends/gnutls.config \
%endif
           --with-default-trust-store-pkcs11="pkcs11:" \
           --without-tpm \
           --without-tpm2 \
%if %{with ktls}
           --enable-ktls \
%else
           --disable-ktls \
%endif
%if %{with dane}
           --with-unbound-root-key-file=/var/lib/unbound/root.key \
           --enable-libdane \
%else
           --disable-libdane \
%endif
%if %{with certificate_compression}
	   --with-zlib --with-brotli --with-zstd \
%else
	   --without-zlib --without-brotli --without-zstd \
%endif
%if %{with liboqs}
           --with-liboqs \
%else
           --without-liboqs \
%endif
           --disable-rpath \
           --with-default-priority-string="@SYSTEM" \
           --disable-doc

%make_build

%install
%make_install -C native_build
pushd native_build

rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la

%if %{without dane}
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/gnutls-dane.pc
%endif

%if %{with fips}
# doing it twice should be a no-op the second time,
# and this way we avoid redefining it and missing a future change
%{__spec_install_post}
fname=`basename $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.30.*.*`
./lib/fipshmac "$RPM_BUILD_ROOT%{_libdir}/libgnutls.so.30" > "$RPM_BUILD_ROOT%{_libdir}/.$fname.hmac"
sed -i "s^$RPM_BUILD_ROOT/usr^^" "$RPM_BUILD_ROOT%{_libdir}/.$fname.hmac"
ln -s ".$fname.hmac" "$RPM_BUILD_ROOT%{_libdir}/.libgnutls.so.30.hmac"
%endif

%if %{with fips}
%define __spec_install_post \
	%{?__debug_package:%{__debug_install_post}} \
	%{__arch_install_post} \
	%{__os_install_post} \
%{nil}
%endif

%if %{without crypto_policies}
# use gnutls configuration file
install -Dm644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/config
%endif

%find_lang gnutls

%check
%if %{with tests}
%if %{with devtoolset}
source /opt/rh/devtoolset-11/enable
%endif

pushd native_build

# KeyUpdate is not yet supported in the kernel.
# p11-kit-trust test are likely to fail in chroot env without root permission and certificate
xfail_tests="ktls_keyupdate.sh p11-kit-trust.sh"

# The ktls.sh test currently only supports kernel 5.11+.  This needs to
# be checked at run time, as the koji builder might be using a different
# version of kernel on the host than the one indicated by the
# kernel-devel package.

case "$(uname -r)" in
  4.* | 5.[0-9].* | 5.10.* )
    xfail_tests="$xfail_tests ktls.sh"
    ;;
esac

make check %{?_smp_mflags} GNUTLS_SYSTEM_PRIORITY_FILE=/dev/null XFAIL_TESTS="$xfail_tests"
popd
%endif

%files -f native_build/gnutls.lang
%{_libdir}/libgnutls.so.30*
%if %{with fips}
%{_libdir}/.libgnutls.so.30*.hmac
%endif
%if %{without crypto_policies}
%{_sysconfdir}/%{name}/config
%endif
%doc README.md AUTHORS NEWS THANKS
%license LICENSE doc/COPYING doc/COPYING.LESSER

%if %{with cxx}
%files c++
%{_libdir}/libgnutlsxx.so.*
%endif

%files devel
%{_includedir}/*
%{_libdir}/libgnutls*.so

%{_libdir}/pkgconfig/*.pc

%files utils
%{_bindir}/certtool
%{_bindir}/ocsptool
%{_bindir}/psktool
%{_bindir}/p11tool
%if %{with srp}
%{_bindir}/srptool
%endif
%if %{with dane}
%{_bindir}/danetool
%endif
%{_bindir}/gnutls*

%if %{with dane}
%files dane
%{_libdir}/libgnutls-dane.so.*
%endif

%changelog
* Wed Feb 25 2026 Philippe Coval <philippe.coval@vates.tech> - 3.8.8-3.1
- Rebase on 3.8.8
- *** Upstream changelog ***
  * Tue Nov 11 2025 Lin Liu <lin.liu01@citrix.com> - 3.8.8-3
  - CP-310102: Build compatible with XS8
  * Tue Jan 21 2025 Alex Brett <alex.brett@cloud.com> - 3.8.8-2
  - CA-405051: Resync with upstream
  * Thu Jan 16 2025 Lin Liu <lin.liu@citrix.com> - 3.8.8-1
  - CP-53173: Update to 3.8.8-1, disable bootstrap and enable LTO
  * Wed Oct 09 2024 AshwinH <ashwin.h@cloud.com> - 3.8.0-2
  - Removed legacy package softhsm
  * Wed Jul 05 2023 Lin Liu <lin.liu@citrix.com> - 3.8.0-1
  - First imported release

* Thu Feb 12 2026 Philippe Coval <philippe.coval@vates.tech> - 3.3.29-10.1
- Remove installed gnutls-dane if no more supported
- Remove unnecessary removal of non built files
- Make c++ lib optional (disabled by default)

* Mon Oct 21 2024 Deli Zhang <deli.zhang@citrix.com> - 3.3.29-10
- First imported release
