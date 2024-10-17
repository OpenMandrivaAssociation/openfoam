%define		name		openfoam
%define		version		2.1.0
%define		openfoam_name	OpenFOAM-%{version}
%define		foam_inst_dir	%{_datadir}/%{name}
%define		openfoam_dir	%{foam_inst_dir}/%{openfoam_name}
%define		thirdparty_name	ThirdParty-%{version}
%define		thirdparty_dir	%{foam_inst_dir}/%{thirdparty_name}

%define		build_paraview	1

Name:		%{name}
Version:	%{version}
Release:	%mkrel 2
Group:		Sciences/Physics
License:	GPL
Summary:	OpenFOAM(r): open source CFD
URL:		https://www.opencfd.co.uk/openfoam/
Source0:	http://downloads.sourceforge.net/foam/OpenFOAM-%{version}.tgz
Source1:	http://downloads.sourceforge.net/foam/ThirdParty-%{version}.tgz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	cmake
BuildRequires:	GL-devel
BuildRequires:	gmp-devel
BuildRequires:	gnuplot
BuildRequires:	hdf5-devel
BuildRequires: 	libtiff-devel
BuildRequires:	libxt-devel
BuildRequires:	mpfr-devel
BuildRequires:	openmpi-devel
BuildRequires:	paraview-mpi paraview-devel
BuildRequires:	python-devel
BuildRequires:	qt4-devel
BuildRequires:	qt4-assistant
BuildRequires:	metis-devel
BuildRequires:	readline-devel
BuildRequires:	scotch-devel
BuildRequires:	tk-devel
BuildRequires:	zlib-devel

Requires:	task-c-devel

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

. %{openfoam_name}/etc/bashrc

%if %{build_paraview}
    # Build paraview first as it is not built by default.
    pushd %{thirdparty_name}
	sh ./makeParaView
    popd
%endif

pushd %{openfoam_name}
    sh ./Allwmake
popd

#-----------------------------------------------------------------------
%install
# Match binaries distributed by upstream (reducing from 800+ to 300+ Mb install)
find %{openfoam_name}/applications \( -name \*.o -o -name \*.dep \) | xargs rm -f
find %{openfoam_name}/src \( -name \*.o -o -name \*.dep \) | xargs rm -f
%ifarch x86_64
LIBDIR=linux64GccDPOpt
%else
LIBDIR=linuxGccDPOpt
%endif
for make in `find %{openfoam_name} -name Make`; do
    rm -fr $make/$LIBDIR
done
mkdir -p %{buildroot}%{foam_inst_dir}
cp -fpar %{openfoam_name} %{buildroot}%{foam_inst_dir}

perl -pi -e "s|(libdir=').*(/ThirdParty.*)|$1%{foam_inst_dir}$2|;"	\
    `find %{thirdparty_name}/platforms -name \*.la`
mkdir -p %{buildroot}%{thirdparty_dir}
cp -fpar %{thirdparty_name}/platforms %{buildroot}%{thirdparty_dir}

# avoid dependency on /usr/xpg4/bin/sh
rm -f %{buildroot}%{openfoam_dir}/bin/tools/replaceAllShellSun

# correct permissions
find %{buildroot}%{openfoam_dir} -perm 0640 | xargs chmod 0644
find %{buildroot}%{openfoam_dir} -perm 0750 | xargs chmod 0755

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/sh

export FOAM_INST_DIR=%{foam_inst_dir}
export PS1="%{openfoam_name}:\u@\h:\W: "
. %{openfoam_dir}/etc/bashrc
if [ ! -d \$FOAM_RUN ]; then
    mkdir -p \$FOAM_RUN
    cp -r \$FOAM_TUTORIALS \$FOAM_RUN 
fi
cd \$FOAM_RUN
exec /bin/bash
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

#-----------------------------------------------------------------------
%files
%defattr(-,root,root)
%{_bindir}/%{name}
%{foam_inst_dir}
