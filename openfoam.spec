%define		version		1.7.1
%define		openfoam_name	OpenFOAM-%{version}
%define		openfoam_dir	%{_datadir}/%{openfoam_name}

Name:		openfoam
Version:	%{version}
Release:	%mkrel 1
Group:		Sciences/Physics
License:	GPL
Summary:	OpenFOAM(r): open source CFD
URL:		http://www.opencfd.co.uk/openfoam/
Source0:	http://downloads.sourceforge.net/foam/OpenFOAM-1.7.1.gtgz
Source1:	http://downloads.sourceforge.net/foam/ThirdParty-1.7.1.gtgz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	gmp-devel
BuildRequires:	mpfr-devel
BuildRequires:	openmpi-devel
BuildRequires:	paraview-mpi paraview-devel
BuildRequires:	qt4-devel
BuildRequires:	metis-devel
BuildRequires:	scotch-devel

Requires:	paraview-mpi

%description
OpenFOAM is a free, open source CFD software package produced by a
commercial company, OpenCFD Ltd. It has a large user base across most
areas of engineering and science, from both commercial and academic
organisations. OpenFOAM has an extensive range of features to solve
anything from complex fluid flows involving chemical reactions,
turbulence and heat transfer, to solid dynamics and electromagnetics.

#-----------------------------------------------------------------------
%prep
tar zxf %{SOURCE0}
tar zxf %{SOURCE1}

#-----------------------------------------------------------------------
%build
export FOAM_INST_DIR=%{_builddir}
pushd %{openfoam_name}
    . etc/bashrc
    sh ./Allwmake
popd

#-----------------------------------------------------------------------
%install
# Match binaries distributed by upstream (reducing from 800+ to 300+ Mb install)
find %{_builddir}/%{openfoam_name}/applications \( -name \*.o -o -name \*.dep \) | xargs rm -f
find %{_builddir}/%{openfoam_name}/src \( -name \*.o -o -name \*.dep \) | xargs rm -f
%ifarch x86_64
LIBDIR=linux64GccDPOpt
%else
LIBDIR=linux32GccDPOpt
%endif
for make in `find %{_builddir}/%{openfoam_name} -name Make`; do
    rm -fr $make/$LIBDIR
done

mkdir -p %{buildroot}%{_datadir}
cp -fpar %{_builddir}/%{openfoam_name} %{buildroot}%{_datadir}

# avoid dependency on /usr/xpg4/bin/sh
rm -f %{buildroot}%{openfoam_dir}/bin/tools/replaceAllShellSun

# correct permissions
find %{buildroot}%{openfoam_dir} -perm 0640 | xargs chmod 0644
find %{buildroot}%{openfoam_dir} -perm 0750 | xargs chmod 0755

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/sh

export FOAM_INST_DIR=%{_datadir}
export PS1="%{openfoam_name}:\u@\h:\W: "
. %{openfoam_dir}/etc/bashrc
exec /bin/bash
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

#-----------------------------------------------------------------------
%files
%defattr(-,root,root)
%{_bindir}/%{name}
%{openfoam_dir}
