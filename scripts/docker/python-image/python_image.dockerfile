FROM python:3

# Create workspace
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app
COPY /scripts/docker/python-image/python_image_requirements.txt /usr/src/app/

# Install python modules from scripts/docker/python-image/python_image_requirements.txt
RUN pip3 install --no-cache-dir pip==23.3.2 && \
    pip3 install --no-cache-dir --requirement python_image_requirements.txt && \
    python -m pip list

# User required for Image DR Check
ARG USER_ID=40514
RUN echo "$USER_ID:!::0:::::" >>/etc/shadow

ARG USER_NAME="eric-oss-common-ci-python"
RUN echo "$USER_ID:x:$USER_ID:0:An Identity for $USER_NAME:/nonexistent:/bin/false" >>/etc/passwd
USER $USER_ID

# Labels required for Image DR Check
LABEL \
    org.opencontainers.image.title=eric-oss-common-ci-python \
    org.opencontainers.image.created="n/a" \
    org.opencontainers.image.revision="n/a" \
    org.opencontainers.image.vendor=Ericsson \
    org.opencontainers.image.version="n/a" \
    com.ericsson.base-image.product-name="n/a" \
    com.ericsson.base-image.product-number="n/a" \
    com.ericsson.base-image.product-version="n/a" \
    com.ericsson.product-revision="n/a" \
    com.ericsson.product-number=CXC90001 \
    author="The Hummingbirds"