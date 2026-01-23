## START: Set by rpmautospec
## (rpmautospec version 0.7.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 4;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%define srpmhash() %{lua:
local files = rpm.expand("%_specdir/gnutls.spec")
for i, p in ipairs(patches) do
   files = files.." "..p
end
for i, p in ipairs(sources) do
   files = files.." "..p
end
local sha256sum = assert(io.popen("cat "..files.."| sha256sum"))
local hash = sha256sum:read("*a")
sha256sum:close()
print(string.sub(hash, 0, 16))
}

Version: 3.8.8
Release: %{?autorelease}%{!?autorelease:1%{?dist}}
Patch: gnutls-3.2.7-rpath.patch

# follow https://gitlab.com/gnutls/gnutls/-/issues/1443
Patch: gnutls-3.8.8-tests-ktls-skip-tls12-chachapoly.patch

%bcond_without bootstrap
%bcond_without dane
%bcond_without fips
%bcond_with tpm12
%bcond_without tpm2
%if 0%{?rhel} >= 9
%bcond_with gost
%else
%bcond_without gost
%endif
%bcond_without certificate_compression
%bcond_without liboqs
%bcond_without tests

%if 0%{?fedora} && 0%{?fedora} < 38
%bcond_without srp
%else
%bcond_with srp
%endif

%if 0%{?fedora}
%bcond_without mingw
%else
%bcond_with mingw
%endif

%if 0%{?rhel} >= 9 && %{with fips}
%bcond_without bundled_gmp
%else
%bcond_with bundled_gmp
%endif


%define fips_requires() %{lua:
local f = assert(io.popen("rpm -q --queryformat '%{EVR}' --whatprovides "..rpm.expand("'%1%{?_isa}'")))
local v = f:read("*all")
f:close()
print("Requires: "..rpm.expand("%1%{?_isa}").." = "..v.."\\n")
}

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
BuildRequires: nettle-devel >= 3.10
%if %{with tpm12}
BuildRequires: trousers-devel >= 0.3.11.2
%endif
%if %{with tpm2}
BuildRequires: tpm2-tss-devel >= 3.0.3
%endif
BuildRequires: libidn2-devel
BuildRequires: libunistring-devel
BuildRequires: net-tools, softhsm, gcc, gcc-c++
BuildRequires: gnupg2
BuildRequires: git-core

# for a sanity check on cert loading
BuildRequires: p11-kit-trust, ca-certificates
Requires: crypto-policies
Requires: p11-kit-trust
Requires: libtasn1 >= 4.3
# always bump when a nettle release is packaged
Requires: nettle >= 3.10
%if %{with tpm12}
Recommends: trousers >= 0.3.11.2
%endif

%if %{with dane}
BuildRequires: unbound-devel unbound-libs
%endif
BuildRequires: make gtk-doc

%if %{with mingw}
BuildRequires:  mingw32-cpp
BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-libtasn1 >= 4.3
BuildRequires:  mingw32-readline
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-nettle >= 3.6
BuildRequires:  mingw64-cpp
BuildRequires:  mingw64-filesystem >= 95
BuildRequires:  mingw64-gcc
BuildRequires:  mingw64-gcc-c++
BuildRequires:  mingw64-libtasn1 >= 4.3
BuildRequires:  mingw64-readline
BuildRequires:  mingw64-zlib
BuildRequires:  mingw64-nettle >= 3.6
%endif

URL: http://www.gnutls.org/
%define short_version %(echo %{version} | grep -m1 -o "[0-9]*\.[0-9]*" | head -1)
Source0: https://www.gnupg.org/ftp/gcrypt/gnutls/v%{short_version}/%{name}-%{version}.tar.xz
Source1: https://www.gnupg.org/ftp/gcrypt/gnutls/v%{short_version}/%{name}-%{version}.tar.xz.sig
Source2: https://gnutls.org/gnutls-release-keyring.gpg

%if %{with bundled_gmp}
Source100:	gmp-6.2.1.tar.xz
# Taken from the main gmp package
Source101:	gmp-6.2.1-intel-cet.patch
Source102:	gmp-6.2.1-c23.patch
%endif

%if 0%{?rhel} >= 10
Source201:	gnutls-3.8.8-tests-rsa-default.patch
%endif

# Wildcard bundling exception https://fedorahosted.org/fpc/ticket/174
Provides: bundled(gnulib) = 20130424

%package c++
Summary: The C++ interface to GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}

%package devel
Summary: Development files for the %{name} package
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-c++%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif
Requires: pkgconfig

%package utils
License: GPL-3.0-or-later
Summary: Command line tools for TLS protocol
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif

%if %{with dane}
%package dane
Summary: A DANE protocol implementation for GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}
%endif

%if %{with fips}
%package fips
Summary: Virtual package to install packages required to use %{name} under FIPS mode
Requires: %{name}%{?_isa} = %{version}-%{release}
%{fips_requires nettle}
%if !%{with bundled_gmp}
%{fips_requires gmp}
%endif
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

%if %{with fips}
%description fips
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures.
This package does not contain any file, but installs required packages
to use GnuTLS under FIPS mode.
%endif

%if %{with mingw}
%package -n mingw32-%{name}
Summary:        MinGW GnuTLS TLS/SSL encryption library
Requires:       pkgconfig
Requires:       mingw32-libtasn1 >= 4.3
BuildArch:      noarch

%description -n mingw32-gnutls
GnuTLS TLS/SSL encryption library.  This library is cross-compiled
for MinGW.

%package -n mingw64-%{name}
Summary:        MinGW GnuTLS TLS/SSL encryption library
Requires:       pkgconfig
Requires:       mingw64-libtasn1 >= 4.3
BuildArch:      noarch

%description -n mingw64-gnutls
GnuTLS TLS/SSL encryption library.  This library is cross-compiled
for MinGW.

%{?mingw_debug_package}
%endif

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'

%autosetup -p1 -S git

%if %{with bundled_gmp}
mkdir -p bundled_gmp
pushd bundled_gmp
tar --strip-components=1 -xf %{SOURCE100}
patch -p1 < %{SOURCE101}
patch -p1 < %{SOURCE102}
popd
%endif

%if 0%{?rhel} >= 10
patch -p1 < %{SOURCE201}
%endif

%build
%define _lto_cflags %{nil}

%if %{with bundled_gmp}
pushd bundled_gmp
autoreconf -ifv
%configure --disable-cxx --disable-shared --enable-fat --with-pic
%make_build
popd

export GMP_CFLAGS="-I$PWD/bundled_gmp"
export GMP_LIBS="$PWD/bundled_gmp/.libs/libgmp.a"
%endif

%if %{with bootstrap}
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
%ifarch %{ix86}
           --disable-year2038 \
%endif
	   --enable-sha1-support \
           --disable-static \
           --disable-openssl-compatibility \
           --disable-non-suiteb-curves \
           --with-system-priority-file=%{_sysconfdir}/crypto-policies/back-ends/gnutls.config \
           --with-default-trust-store-pkcs11="pkcs11:" \
%if %{with tpm12}
           --with-trousers-lib=%{_libdir}/libtspi.so.1 \
%else
           --without-tpm \
%endif
%if %{with tpm2}
           --with-tpm2 \
%else
           --without-tpm2 \
%endif
           --enable-ktls \
           --htmldir=%{_docdir}/manual \
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
           --with-default-priority-string="@SYSTEM"

%make_build
popd

%if %{with mingw}
# MinGW does not support CCASFLAGS
export CCASFLAGS=""
%mingw_configure \
%if %{with srp}
    --enable-srp-authentication \
%endif
    --enable-sha1-support \
    --disable-static \
    --disable-openssl-compatibility \
    --disable-non-suiteb-curves \
    --disable-libdane \
    --disable-rpath \
    --disable-nls \
    --disable-cxx \
    --enable-shared \
    --without-tpm \
    --with-included-unistring \
    --disable-doc \
    --with-default-priority-string="@SYSTEM" \
    --without-p11-kit
%mingw_make %{?_smp_mflags}
%endif

%install
%make_install -C native_build
pushd native_build
make -C doc install-html DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
%if %{without dane}
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/gnutls-dane.pc
%endif

%if %{with fips}
# doing it twice should be a no-op the second time,
# and this way we avoid redefining it and missing a future change
%global __debug_package 1
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

%find_lang gnutls
popd

%if %{with mingw}
%mingw_make_install

# Remove .la files
rm -f $RPM_BUILD_ROOT%{mingw32_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{mingw64_libdir}/*.la

# The .def files aren't interesting for other binaries
rm -f $RPM_BUILD_ROOT%{mingw32_bindir}/*.def
rm -f $RPM_BUILD_ROOT%{mingw64_bindir}/*.def

# Remove info and man pages which duplicate stuff in Fedora already.
rm -rf $RPM_BUILD_ROOT%{mingw32_infodir}
rm -rf $RPM_BUILD_ROOT%{mingw32_mandir}
rm -rf $RPM_BUILD_ROOT%{mingw32_docdir}/gnutls

rm -rf $RPM_BUILD_ROOT%{mingw64_infodir}
rm -rf $RPM_BUILD_ROOT%{mingw64_mandir}
rm -rf $RPM_BUILD_ROOT%{mingw64_docdir}/gnutls

# Remove test libraries
rm -f $RPM_BUILD_ROOT%{mingw32_libdir}/crypt32.dll*
rm -f $RPM_BUILD_ROOT%{mingw32_libdir}/ncrypt.dll*
rm -f $RPM_BUILD_ROOT%{mingw64_libdir}/crypt32.dll*
rm -f $RPM_BUILD_ROOT%{mingw64_libdir}/ncrypt.dll*

%mingw_debug_install_post
%endif

%check
%if %{with tests}
pushd native_build

# KeyUpdate is not yet supported in the kernel.
xfail_tests=ktls_keyupdate.sh

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
%doc README.md AUTHORS NEWS THANKS
%license LICENSE doc/COPYING doc/COPYING.LESSER

%files c++
%{_libdir}/libgnutlsxx.so.*

%files devel
%{_includedir}/*
%{_libdir}/libgnutls*.so

%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*
%{_infodir}/gnutls*
%{_infodir}/pkcs11-vision*
%{_docdir}/manual/*

%files utils
%{_bindir}/certtool
%if %{with tpm12}
%{_bindir}/tpmtool
%endif
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
%{_mandir}/man1/*
%doc doc/certtool.cfg

%if %{with dane}
%files dane
%{_libdir}/libgnutls-dane.so.*
%endif

%if %{with fips}
%files fips
%endif

%if %{with mingw}
%files -n mingw32-%{name}
%license LICENSE doc/COPYING doc/COPYING.LESSER
%{mingw32_bindir}/certtool.exe
%{mingw32_bindir}/gnutls-cli-debug.exe
%{mingw32_bindir}/gnutls-cli.exe
%{mingw32_bindir}/gnutls-serv.exe
%{mingw32_bindir}/libgnutls-30.dll
%{mingw32_bindir}/ocsptool.exe
#%%{mingw32_bindir}/p11tool.exe
%{mingw32_bindir}/psktool.exe
%if %{with srp}
%{mingw32_bindir}/srptool.exe
%endif
%{mingw32_libdir}/libgnutls.dll.a
%{mingw32_libdir}/libgnutls-30.def
%{mingw32_libdir}/pkgconfig/gnutls.pc
%{mingw32_includedir}/gnutls/

%files -n mingw64-%{name}
%license LICENSE doc/COPYING doc/COPYING.LESSER
%{mingw64_bindir}/certtool.exe
%{mingw64_bindir}/gnutls-cli-debug.exe
%{mingw64_bindir}/gnutls-cli.exe
%{mingw64_bindir}/gnutls-serv.exe
%{mingw64_bindir}/libgnutls-30.dll
%{mingw64_bindir}/ocsptool.exe
#%%{mingw64_bindir}/p11tool.exe
%{mingw64_bindir}/psktool.exe
%if %{with srp}
%{mingw64_bindir}/srptool.exe
%endif
%{mingw64_libdir}/libgnutls.dll.a
%{mingw64_libdir}/libgnutls-30.def
%{mingw64_libdir}/pkgconfig/gnutls.pc
%{mingw64_includedir}/gnutls/
%endif

%changelog
## START: Generated by rpmautospec
* Wed Feb 05 2025 Yaakov Selkowitz <yselkowi@redhat.com> - 3.8.8-4
- Fix ELN build

* Thu Jan 23 2025 Daiki Ueno <dueno@redhat.com> - 3.8.8-3
- Disable GOST in RHEL-9 or later

* Thu Jan 16 2025 Fedora Release Engineering <releng@fedoraproject.org> - 3.8.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Tue Nov 05 2024 Daiki Ueno <dueno@redhat.com> - 3.8.8-1
- Update to 3.8.8 upstream release
- Resolves: rhbz#2323786

* Tue Nov 05 2024 Daiki Ueno <dueno@redhat.com> - 3.8.7-7
- Fix build with latest mingw-gcc

* Tue Nov 05 2024 Daiki Ueno <dueno@redhat.com> - 3.8.7-6
- Update downstream patches for 3.8.8

* Tue Nov 05 2024 Daiki Ueno <dueno@redhat.com> - 3.8.7-5
- Remove distribution suffix before updating to 3.8.8

* Fri Sep 13 2024 Richard W.M. Jones <rjones@redhat.com> - 3.8.7-4
- Remove mingw p11tool.exe

* Thu Sep 12 2024 Richard W.M. Jones <rjones@redhat.com> - 3.8.7-3
- Remove mingw-p11-kit dependency (RHBZ#2312031)

* Fri Aug 16 2024 Daiki Ueno <dueno@redhat.com> - 3.8.7-2
- Stop pulling in compression libraries through gnutls.pc

* Thu Aug 15 2024 Daiki Ueno <dueno@redhat.com> - 3.8.7-1
- Update to 3.8.7 upstream release
- Resolves: rhbz#2305086

* Thu Aug 15 2024 Daiki Ueno <dueno@redhat.com> - 3.8.6-9
- Remove upstreamed patches before updating to 3.8.7

* Mon Jul 29 2024 Daiki Ueno <dueno@redhat.com> - 3.8.6-8
- liboqs: check whether Kyber768 is compiled in

* Fri Jul 26 2024 Daiki Ueno <dueno@redhat.com> - 3.8.6-7
- Fix configure check on nettle_rsa_oaep_* functions

* Wed Jul 24 2024 Daiki Ueno <dueno@redhat.com> - 3.8.6-6
- Enable X25519Kyber768Draft00 key exchange in TLS

* Mon Jul 22 2024 Daiki Ueno <dueno@redhat.com> - 3.8.6-5
- Switch to using dlwrap for loading compression libraries

* Fri Jul 19 2024 Yaakov Selkowitz <yselkowi@redhat.com> - 3.8.6-4
- Fix FIPS build with RPM 4.20

* Thu Jul 18 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.8.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Mon Jul 08 2024 Daiki Ueno <dueno@redhat.com> - 3.8.6-2
- Bump nettle dependency to 3.10

* Wed Jul 03 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.6-1
- Update to 3.8.6 upstream release

* Mon Jun 17 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.5-6
- Build with certificate compression enabled

* Mon Jun 17 2024 Daiki Ueno <dueno@redhat.com> - 3.8.5-5
- Bump release to build against newer nettle

* Thu May 16 2024 Alexander Sosedkin <asosedkin@redhat.com> - 3.8.5-4
- Add gmp tarball to sources file, add gmp patch

* Tue May 14 2024 Daiki Ueno <dueno@redhat.com> - 3.8.5-3
- Add bcond to statically link to GMP

* Wed Apr 24 2024 Daiki Ueno <dueno@redhat.com> - 3.8.5-2
- Add virtual package to pull in nettle/gmp dependencies for FIPS

* Thu Apr 04 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.5-1
- [packit] 3.8.5 upstream release

* Wed Mar 20 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.4-1
- [packit] 3.8.4 upstream release
- Resolves rhbz#2270320

* Thu Feb 22 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.3-3
- Fix mingw build failure

* Wed Jan 24 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.3-2
- Update keyring

* Tue Jan 23 2024 Zoltan Fridrich <zfridric@redhat.com> - 3.8.3-1
- [packit] 3.8.3 upstream release

* Fri Jan 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.8.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Tue Dec 12 2023 Simon de Vlieger <cmdr@supakeen.com> - 3.8.2-3
- Bump Nettle dependency.

* Fri Dec 01 2023 Daiki Ueno <dueno@redhat.com> - 3.8.2-2
- Tentatively revert newly added Ed448 keys support in PKCS#11

* Wed Nov 22 2023 Daiki Ueno <dueno@redhat.com> - 3.8.2-1
- [packit] 3.8.2 upstream release

* Wed Nov 22 2023 Daiki Ueno <dueno@redhat.com> - 3.8.1-4
- Remove patches no longer needed in 3.8.2

* Thu Nov 09 2023 Daiki Ueno <dueno@redhat.com> - 3.8.1-3
- Skip KTLS test if the host kernel is older than 5.11

* Tue Aug 29 2023 Stephen Gallagher <sgallagh@redhat.com> - 3.8.1-2
- Don't build with SRP on RHEL

* Fri Aug 25 2023 Zoltan Fridrich <zfridric@redhat.com> - 3.8.1-1
- [packit] 3.8.1 upstream release

* Thu Aug 24 2023 Daiki Ueno <dueno@redhat.com> - 3.8.0-8
- Migrate License field to SPDX license identifier

* Wed Jul 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 3.8.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue May 23 2023 Peter Leitmann <peto.leitmann@gmail.com> - 3.8.0-6
- Add TMT interop tests

* Thu Apr 13 2023 Daiki Ueno <dueno@redhat.com> - 3.8.0-5
- Fix leftover of the previous %%bcond change

* Tue Apr 11 2023 Daiki Ueno <dueno@redhat.com> - 3.8.0-4
- Use %%bcond instead of %%global for srp and mingw support

* Sat Mar 11 2023 Richard W.M. Jones <rjones@redhat.com> - 3.8.0-3
- Fix desychronisation with kTLS:
  https://gitlab.com/gnutls/gnutls/-/issues/1470

* Thu Mar 02 2023 Daniel P. Berrangé <berrange@redhat.com> - 3.8.0-2
- Disable GNULIB's year2038 support for 64-bit time_t

* Thu Feb 16 2023 Zoltan Fridrich <zfridric@redhat.com> - 3.8.0-1
- [packit] 3.8.0 upstream release

* Tue Feb 14 2023 Zoltan Fridrich <zfridric@redhat.com> - 3.7.8-14
- Prepare for release

* Fri Jan 20 2023 Frantisek Krenzelok <krenzelok.frantisek@gmail.com> - 3.7.8-13
- KTLS: disable ktls_keyupdate & tls1.2 chachapoly tests

* Fri Jan 20 2023 Frantisek Krenzelok <krenzelok.frantisek@gmail.com> - 3.7.8-12
- KTLS additional ciphersuites

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.8-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Wed Dec 14 2022 Frantisek Krenzelok <krenzelok.frantisek@gmail.com> - 3.7.8-10
- gcc-analyzer: suppress warnings

* Thu Oct 27 2022 Daniel P. Berrangé <berrange@redhat.com> - 3.7.8-9
- Cross-compiled mingw sub-RPMs should be 'noarch'

* Wed Oct 19 2022 Zoltan Fridrich <zfridric@redhat.com> - 3.7.8-8
- Add conditions for mingw

* Tue Oct 18 2022 Michael Cronenworth <mike@cchtml.com> - 3.7.8-6
- Initial MinGW package support

* Tue Oct 18 2022 Zoltan Fridrich <zfridric@redhat.com> - 3.7.8-5
- Use make macros

* Tue Oct 18 2022 Zoltan Fridrich <zfridric@redhat.com> - 3.7.8-4
- RPMAUTOSPEC: unresolvable merge
## END: Generated by rpmautospec
