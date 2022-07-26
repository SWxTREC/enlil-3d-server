# ARG BASE_IMAGE=ubuntu:20.04

ARG BASE_IMAGE=nvidia/opengl:1.0-glvnd-devel-ubuntu20.04
FROM ${BASE_IMAGE}

USER root

# Need to force noninteractive for apt-get updates
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        apache2-dev \
        apache2 \
        libapr1-dev \
        apache2-utils \
        python3-dev \
        python3-pip \
        python3-setuptools \
        sudo && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd proxy-mapping && \
    groupadd pvw-user && \
    useradd --system -g pvw-user -G proxy-mapping -s /sbin/nologin pvw-user && \
    usermod -a -G proxy-mapping www-data && \
    useradd admin && echo "admin:admin" | chpasswd && adduser admin sudo && \
    mkdir -p /opt/launcher/log && \
    chown -R pvw-user:pvw-user /opt/launcher && \
    mkdir -p /opt/paraviewweb/scripts && \
    touch /opt/launcher/proxy-mapping.txt && \
    chown pvw-user:proxy-mapping /opt/launcher/proxy-mapping.txt && \
    chmod 660 /opt/launcher/proxy-mapping.txt

# Copy the apache configuration file into place
COPY config/apache/001-pvw.conf /etc/apache2/sites-available/001-pvw.conf

# Copy the script into place
COPY scripts/start.sh /opt/paraviewweb/scripts/
COPY scripts/addEndpoints.sh /opt/paraviewweb/scripts/
COPY scripts/server.sh /opt/paraviewweb/scripts/

# Configure the apache web server
RUN a2enmod vhost_alias && \
    a2enmod proxy && \
    a2enmod proxy_http && \
    a2enmod proxy_wstunnel && \
    a2enmod rewrite && \
    a2enmod headers && \
    a2dissite 000-default.conf && \
    a2ensite 001-pvw.conf

# Open port 80 to the world outside the container
EXPOSE 80

# Copy the launcher config template
COPY config/launcher/config.json /opt/launcher/config-template.json

#
# Now we run this script which will update the apache vhost file.  We use bash
# instead of "sh" due to the use of "read -d" in the script.  Also, it is bash, not
# docker which manages the env variable interpolation, so we must use bash if we
# want that convenience.
#
# To add more endpoints, simply add more pairs of arguments beyond "visualizer" and
# "/opt/paraview/.../www".
#

# Copy in the tar file, extract it, then rename it /opt/paraview/...
# COPY binaries/ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz /opt
# RUN cd /opt && \
#     tar -xzvf ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz && \
#     mv ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit paraview

COPY binaries/ParaView-5.9.1-egl-MPI-Linux-Python3.8-64bit.tar.gz /opt
RUN cd /opt && \
    tar -xzvf ParaView-5.9.1-egl-MPI-Linux-Python3.8-64bit.tar.gz && \
    mv ParaView-5.9.1-egl-MPI-Linux-Python3.8-64bit paraview

# Replacing a bad wslink file
# COPY extras/launcher.py /opt/paraview/lib/python3.8/site-packages/wslink/
# Install missing packages
RUN pip install --target=/opt/paraview/lib/python3.8/site-packages/ --upgrade wslink cryptography

# RUN ["/opt/paraviewweb/scripts/addEndpoints.sh", \
#   "h3lioviz", "/opt/paraview/share/paraview-5.9/web/visualizer/www" \
# ]

# Start the container.  If we're not running this container, but rather are
# building other containers based on it, this entry point can/should be
# overridden in the child container.  In that case, use the "start.sh"
# script instead, or you can provide a custom one.
ENTRYPOINT ["/opt/paraviewweb/scripts/server.sh"]
