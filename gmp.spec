#
# Important for %{ix86}:
# This rpm has to be build on a CPU with sse2 support like Pentium 4 !
#

Summary: A GNU arbitrary precision library
Name: gmp
Version: 4.3.2
Release: 6
URL: http://gmplib.org/
Source0: ftp://ftp.gnu.org/pub/gnu/gmp/gmp-%{version}.tar.bz2
Source2: gmp.h
Source3: gmp-mparam.h
#Patch1: gmp-4.2.4-no-host-target-check.patch
Patch11: gmp-4.1.4-noexecstack.patch
Patch12: arm-binutils-hack.patch
Patch13: tscan.patch
Patch14: disable_am_c_prototypes.patch
License: LGPLv3+
Group: System/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: autoconf automake libtool

%description
The gmp package contains GNU MP, a library for arbitrary precision
arithmetic, signed integers operations, rational numbers and floating
point numbers. GNU MP is designed for speed, for both small and very
large operands. GNU MP is fast because it uses fullwords as the basic
arithmetic type, it uses fast algorithms, it carefully optimizes
assembly code for many CPUs' most common inner loops, and it generally
emphasizes speed over simplicity/elegance in its operations.

Install the gmp package if you need a fast arbitrary precision
library.

%package devel
Summary: Development tools for the GNU MP arbitrary precision library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description devel
The libraries, header files and documentation for using the GNU MP 
arbitrary precision library in applications.

If you want to develop applications which will use the GNU MP library,
you'll need to install the gmp-devel package.  You'll also need to
install the gmp package.

%package static
Summary: Development tools for the GNU MP arbitrary precision library
Group: Development/Libraries
Requires: %{name}-devel = %{version}-%{release}

%description static
The static libraries for using the GNU MP arbitrary precision library 
in applications.

%prep
%setup -q 
#%patch1 -p1 -b .no-host-target
%patch11 -p1 -b .mips
%patch12 -p1 -b .arm
%patch13 -p1 -b .tscan
%patch14 -p1

%build
autoreconf -if
if as --help | grep -q execstack; then
  # the object files do not require an executable stack
  export CCAS="gcc -c -Wa,--noexecstack"
fi
mkdir base
cd base
ln -s ../configure .
./configure --build=%{_build} --host=%{_host} \
         --program-prefix=%{?_program_prefix} \
         --prefix=%{_prefix} \
         --exec-prefix=%{_exec_prefix} \
         --bindir=%{_bindir} \
         --sbindir=%{_sbindir} \
         --sysconfdir=%{_sysconfdir} \
         --datadir=%{_datadir} \
         --includedir=%{_includedir} \
         --libdir=%{_libdir} \
         --libexecdir=%{_libexecdir} \
         --localstatedir=%{_localstatedir} \
         --sharedstatedir=%{_sharedstatedir} \
         --mandir=%{_mandir} \
         --infodir=%{_infodir} \
         --enable-mpbsd --enable-cxx
perl -pi -e 's|hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=\"-L\\\$libdir\"|g;' libtool
export LD_LIBRARY_PATH=`pwd`/.libs
make CFLAGS="$RPM_OPT_FLAGS" %{?_smp_mflags}
cd ..
%ifarch %{ix86}
mkdir build-sse2
cd build-sse2
ln -s ../configure .
CFLAGS="%{optflags} -march=pentium4"
./configure --build=%{_build} --host=%{_host} \
         --program-prefix=%{?_program_prefix} \
         --prefix=%{_prefix} \
         --exec-prefix=%{_exec_prefix} \
         --bindir=%{_bindir} \
         --sbindir=%{_sbindir} \
         --sysconfdir=%{_sysconfdir} \
         --datadir=%{_datadir} \
         --includedir=%{_includedir} \
         --libdir=%{_libdir} \
         --libexecdir=%{_libexecdir} \
         --localstatedir=%{_localstatedir} \
         --sharedstatedir=%{_sharedstatedir} \
         --mandir=%{_mandir} \
         --infodir=%{_infodir} \
         --enable-mpbsd --enable-cxx
perl -pi -e 's|hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=\"-L\\\$libdir\"|g;' libtool
export LD_LIBRARY_PATH=`pwd`/.libs
make %{?_smp_mflags}
unset CFLAGS
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT
cd base
export LD_LIBRARY_PATH=`pwd`/.libs
make install DESTDIR=$RPM_BUILD_ROOT
install -m 644 gmp-mparam.h ${RPM_BUILD_ROOT}%{_includedir}
rm -f $RPM_BUILD_ROOT%{_libdir}/lib{gmp,mp,gmpxx}.la
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}
ln -sf libgmpxx.so.4 $RPM_BUILD_ROOT%{_libdir}/libgmpxx.so
cd ..
%ifarch %{ix86}
cd build-sse2
export LD_LIBRARY_PATH=`pwd`/.libs
mkdir $RPM_BUILD_ROOT%{_libdir}/sse2
install -m 755 .libs/libgmp.so.3.* $RPM_BUILD_ROOT%{_libdir}/sse2
cp -a .libs/libgmp.so.3 $RPM_BUILD_ROOT%{_libdir}/sse2
chmod 755 $RPM_BUILD_ROOT%{_libdir}/sse2/libgmp.so.3
install -m 755 .libs/libgmpxx.so.4.* $RPM_BUILD_ROOT%{_libdir}/sse2
cp -a .libs/libgmpxx.so.4 $RPM_BUILD_ROOT%{_libdir}/sse2
chmod 755 $RPM_BUILD_ROOT%{_libdir}/sse2/libgmpxx.so.4
install -m 755 .libs/libmp.so.3.* $RPM_BUILD_ROOT%{_libdir}/sse2
cp -a .libs/libmp.so.3 $RPM_BUILD_ROOT%{_libdir}/sse2
chmod 755 $RPM_BUILD_ROOT%{_libdir}/sse2/libmp.so.3
cd ..
%endif

# Rename gmp.h to gmp-<arch>.h and gmp-mparam.h to gmp-mparam-<arch>.h to 
# avoid file conflicts on multilib systems and install wrapper include files
# gmp.h and gmp-mparam-<arch>.h
basearch=%{_arch}
# always use i386 for iX86
%ifarch %{ix86}
basearch=i386
%endif
# always use arm for arm*
%ifarch %{arm}
basearch=arm
%endif
%ifarch mipsel
basearch=mips
%endif
# superH architecture support
%ifarch sh3 sh4
basearch=sh
%endif
# Rename files and install wrappers

mv %{buildroot}/%{_includedir}/gmp.h %{buildroot}/%{_includedir}/gmp-${basearch}.h
install -m644 %{SOURCE2} %{buildroot}/%{_includedir}/gmp.h
mv %{buildroot}/%{_includedir}/gmp-mparam.h %{buildroot}/%{_includedir}/gmp-mparam-${basearch}.h
install -m644 %{SOURCE3} %{buildroot}/%{_includedir}/gmp-mparam.h


%check
%ifnarch aarch64 ppc
cd base
export LD_LIBRARY_PATH=`pwd`/.libs
make %{?_smp_mflags} check
cd ..
%endif
%ifarch %{ix86}
cd build-sse2
export LD_LIBRARY_PATH=`pwd`/.libs
make %{?_smp_mflags} check
cd ..
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel
if [ -f %{_infodir}/gmp.info.gz ]; then
    /sbin/install-info %{_infodir}/gmp.info.gz %{_infodir}/dir || :
fi
exit 0

%preun devel
if [ $1 = 0 ]; then
    if [ -f %{_infodir}/gmp.info.gz ]; then
        /sbin/install-info --delete %{_infodir}/gmp.info.gz %{_infodir}/dir || :
    fi
fi
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc COPYING COPYING.LIB NEWS README
%{_libdir}/libgmp.so.*
%{_libdir}/libmp.so.*
%{_libdir}/libgmpxx.so.*
%ifarch %{ix86}
%{_libdir}/sse2/*
%endif

%files devel
%defattr(-,root,root,-)
%{_libdir}/libmp.so
%{_libdir}/libgmp.so
%{_libdir}/libgmpxx.so
%{_includedir}/*.h
%{_infodir}/gmp.info*

%files static
%defattr(-,root,root,-)
%{_libdir}/libmp.a
%{_libdir}/libgmp.a
%{_libdir}/libgmpxx.a


