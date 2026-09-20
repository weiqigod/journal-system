FROM ehrbase/ehrbase:2.36.0@sha256:c8e642264b73637e0576ec01b5c73f5dc9be6f34eb3644f0ced890c5f916640a AS upstream
FROM eclipse-temurin:25-jdk-alpine@sha256:541729c21f9308a68cebbe5a0627e4cd465dfe8980fc03bac0b2feaee57daafd AS build
WORKDIR /build
COPY --from=upstream /app/ehrbase.jar ./ehrbase.jar
COPY source/ ./source/
# Compile only the changed classes against the exact released dependency jars.
# This is a local experiment build, not an upstream Maven release build.
RUN jar --extract --file ehrbase.jar BOOT-INF/lib \
    && javac --release 25 -parameters -proc:none -cp 'BOOT-INF/lib/*' -d classes \
        source/OpenehrCompositionController.java source/AbstractVersionedObjectRepository.java \
    && jar --update --file BOOT-INF/lib/rest-openehr-2.36.0.jar -C classes org/ehrbase/rest \
    && jar --update --file BOOT-INF/lib/service-2.36.0.jar -C classes org/ehrbase/repository \
    && jar --update --no-compress --file ehrbase.jar \
        BOOT-INF/lib/rest-openehr-2.36.0.jar BOOT-INF/lib/service-2.36.0.jar
FROM upstream
COPY --from=build --chown=ehrbase:ehrbase /build/ehrbase.jar /app/ehrbase.jar
LABEL org.journal.experiment="EHRbase 2.36.0 local concurrency patch; not an upstream release"
