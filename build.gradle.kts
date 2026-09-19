plugins {
    `java-library`
    `maven-publish`
    alias(libs.plugins.protobuf)
}

// JitPack coordinates: com.github.Rise-Newtork:RiseProtocol:<tag>
group = "com.github.Rise-Newtork"
version = "v1.3.0"

repositories {
    mavenCentral()
}

dependencies {
    // api, not implementation: consumers handle the generated messages and stubs directly.
    api(libs.protobuf.java)
    api(libs.grpc.stub)
    api(libs.grpc.protobuf)

    // javax.annotation.Generated, referenced by the generated gRPC stubs but not needed at runtime.
    compileOnly(libs.annotations.api)
}

// The .proto files already sit in src/main/proto, which is the plugin's default
// source directory, so there is nothing to reconfigure. The plugin also copies
// them into the jar, so consumers can import the schema straight out of the artifact.

protobuf {
    protoc {
        artifact = libs.protoc.get().toString()
    }

    plugins {
        create("grpc") {
            artifact = libs.grpc.gen.java.get().toString()
        }
    }

    generateProtoTasks {
        all().forEach { task ->
            task.plugins {
                create("grpc")
            }
        }
    }
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(25)
    }

    withSourcesJar()
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
        }
    }
}
