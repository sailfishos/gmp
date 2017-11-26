#
# Important for %{ix86}:
# This rpm has to be build on a CPU with sse2 support like Pentium 4 !
#

Summary: A GNU arbitrary precision library
Name: gmp
Version: 6.1.2
Release: 1
URL: http://gmplib.org/
Source0: ftp://ftp.gnu.org/pub/gnu/gmp/gmp-%{version}.tar.bz2
Source2: gmp.h
Source3: gmp-mparam.h
Patch11: gmp-4.1.4-noexecstack.patch
License: LGPLv3+ or GPLv2+
Group: System/Libraries
BuildRequires: autoconf automake libtool
Provides: libgmp.so.3

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
%patch11 -p1 -b .mips

%build
autoreconf -if
if as --help | grep -q execstack; then
  # the object files do not require an executable stack
  export CCAS="gcc -c -Wa,--noexecstack"
fi
mkdir base
cd base
ln -s ../configure .
%ifarch %{ix86}
export CFLAGS=$(echo $RPM_OPT_FLAGS | sed -e "s/-mtune=[^ ]*//g" | sed -e "s/-march=[^ ]*//g")" -march=i686"
%endif
./configure --enable-fat --build=%{_build} --host=%{_host} \
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

%install
rm -rf $RPM_BUILD_ROOT
cd base
export LD_LIBRARY_PATH=`pwd`/.libs
make install DESTDIR=$RPM_BUILD_ROOT
install -m 644 gmp-mparam.h ${RPM_BUILD_ROOT}%{_includedir}
rm -f $RPM_BUILD_ROOT%{_libdir}/lib{gmp,mp,gmpxx}.la
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}
ln -sf libgmp.so.10 $RPM_BUILD_ROOT%{_libdir}/libgmp.so.3
ln -sf libgmpxx.so.4 $RPM_BUILD_ROOT%{_libdir}/libgmpxx.so
cd ..

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
%if ! 0%{?qemu_user_space_build}
cd base
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
%doc COPYING* NEWS README
%{_libdir}/libgmp.so.*
%{_libdir}/libgmpxx.so.*

%files devel
%defattr(-,root,root,-)
%{_libdir}/libgmp.so
%{_libdir}/libgmpxx.so
%{_includedir}/*.h
%{_infodir}/gmp.info*

%files static
%defattr(-,root,root,-)
%{_libdir}/libgmp.a
%{_libdir}/libgmpxx.a


