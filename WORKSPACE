# Copyright 2021 The Pigweed Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

workspace(
    name = "pigweed",
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository", "new_git_repository")
load(
    "//pw_env_setup/bazel/cipd_setup:cipd_rules.bzl",
    "cipd_client_repository",
    "cipd_repository",
    "pigweed_deps",
)

# Set up Bazel platforms.
# Required by: pigweed.
# Used in modules: //pw_build, (Assorted modules via select statements).
http_archive(
    name = "platforms",
    sha256 = "5308fc1d8865406a49427ba24a9ab53087f17f5266a7aabbfc28823f3916e1ca",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/platforms/releases/download/0.0.6/platforms-0.0.6.tar.gz",
        "https://github.com/bazelbuild/platforms/releases/download/0.0.6/platforms-0.0.6.tar.gz",
    ],
)

# Setup CIPD client and packages.
# Required by: pigweed.
# Used by modules: all.
pigweed_deps()

load("@cipd_deps//:cipd_init.bzl", "cipd_init")

cipd_init()

cipd_client_repository()

cipd_repository(
    name = "pw_transfer_test_binaries",
    path = "pigweed/pw_transfer_test_binaries/${os=linux}-${arch=amd64}",
    tag = "version:pw_transfer_test_binaries_528098d588f307881af83f769207b8e6e1b57520-linux-amd64-cipd.cipd",
)

# Set up Starlark library.
# Required by: io_bazel_rules_go, com_google_protobuf, rules_python
# Used in modules: None.
# This must be instantiated before com_google_protobuf as protobuf_deps() pulls
# in an older version of bazel_skylib. However io_bazel_rules_go requires a
# newer version.
http_archive(
    name = "bazel_skylib",  # 2022-09-01
    sha256 = "4756ab3ec46d94d99e5ed685d2d24aece484015e45af303eb3a11cab3cdc2e71",
    strip_prefix = "bazel-skylib-1.3.0",
    urls = ["https://github.com/bazelbuild/bazel-skylib/archive/refs/tags/1.3.0.zip"],
)

load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")

bazel_skylib_workspace()

# Set up Python support.
# Required by: rules_fuzzing, com_github_nanopb_nanopb.
# Used in modules: None.
http_archive(
    name = "rules_python",
    sha256 = "0a8003b044294d7840ac7d9d73eef05d6ceb682d7516781a4ec62eeb34702578",
    strip_prefix = "rules_python-0.24.0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.24.0/rules_python-0.24.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "python_register_toolchains")

# Use Python 3.10 for bazel Python rules.
python_register_toolchains(
    name = "python3_10",
    python_version = "3.10",
)

load("@python3_10//:defs.bzl", "interpreter")
load("@rules_python//python:pip.bzl", "pip_parse")

# Specify third party Python package versions with pip_parse.
# pip_parse will generate and expose a repository for each package in the
# requirements_lock file named @python_packages_{PACKAGE}.
pip_parse(
    name = "python_packages",
    python_interpreter_target = interpreter,
    requirements_darwin = "//pw_env_setup/py/pw_env_setup/virtualenv_setup:upstream_requirements_darwin_lock.txt",
    requirements_linux = "//pw_env_setup/py/pw_env_setup/virtualenv_setup:upstream_requirements_linux_lock.txt",
    requirements_windows = "//pw_env_setup/py/pw_env_setup/virtualenv_setup:upstream_requirements_windows_lock.txt",
)

load("@python_packages//:requirements.bzl", "install_deps")

# Run pip install for all @python_packages_*//:pkg deps.
install_deps()

# Set up upstream googletest and googlemock.
# Required by: Pigweed.
# Used in modules: //pw_analog, //pw_fuzzer, //pw_i2c.
http_archive(
    name = "com_google_googletest",
    sha256 = "ad7fdba11ea011c1d925b3289cf4af2c66a352e18d4c7264392fead75e919363",
    strip_prefix = "googletest-1.13.0",
    urls = [
        "https://github.com/google/googletest/archive/refs/tags/v1.13.0.tar.gz",
    ],
)

# Set up host hermetic host toolchain.
# Required by: All cc targets.
# Used in modules: All cc targets.
git_repository(
    name = "rules_cc_toolchain",
    commit = "9f209fda87414285bc66accd3612575b29760fba",
    remote = "https://github.com/bazelembedded/rules_cc_toolchain",
    shallow_since = "1675385535 -0800",
)

load("@rules_cc_toolchain//:rules_cc_toolchain_deps.bzl", "rules_cc_toolchain_deps")

rules_cc_toolchain_deps()

load("@rules_cc_toolchain//cc_toolchain:cc_toolchain.bzl", "register_cc_toolchains")

register_cc_toolchains()

# Sets up Bazels documentation generator.
# Required by: rules_cc_toolchain.
# Required by modules: All
git_repository(
    name = "io_bazel_stardoc",
    commit = "2b801dc9b93f73812948ee4e505805511b0f55dc",
    remote = "https://github.com/bazelbuild/stardoc.git",
    shallow_since = "1651081130 -0400",
)

# Set up Protobuf rules.
# Required by: pigweed.
# Used in modules: //pw_protobuf.
http_archive(
    name = "com_google_protobuf",
    sha256 = "c6003e1d2e7fefa78a3039f19f383b4f3a61e81be8c19356f85b6461998ad3db",
    strip_prefix = "protobuf-3.17.3",
    url = "https://github.com/protocolbuffers/protobuf/archive/v3.17.3.tar.gz",
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()

# Setup Nanopb protoc plugin.
# Required by: Pigweed.
# Used in modules: pw_protobuf.
git_repository(
    name = "com_github_nanopb_nanopb",
    commit = "ee27d70d329e1718f39eea1f425178e747263173",
    remote = "https://github.com/nanopb/nanopb.git",
    shallow_since = "1641373017 +0800",
)

load("@com_github_nanopb_nanopb//extra/bazel:nanopb_deps.bzl", "nanopb_deps")

nanopb_deps()

load("@com_github_nanopb_nanopb//extra/bazel:python_deps.bzl", "nanopb_python_deps")

nanopb_python_deps(interpreter)

load("@com_github_nanopb_nanopb//extra/bazel:nanopb_workspace.bzl", "nanopb_workspace")

nanopb_workspace()

# Set up embedded C/C++ toolchains.
# Required by: pigweed.
# Used in modules: //pw_polyfill, //pw_build (all pw_cc* targets).
git_repository(
    name = "bazel_embedded",
    commit = "91dcc13ebe5df755ca2fe896ff6f7884a971d05b",
    remote = "https://github.com/bazelembedded/bazel-embedded.git",
    shallow_since = "1631751909 +0800",
)

# Configure bazel_embedded toolchains and platforms.
load(
    "@bazel_embedded//:bazel_embedded_deps.bzl",
    "bazel_embedded_deps",
)

bazel_embedded_deps()

load(
    "@bazel_embedded//platforms:execution_platforms.bzl",
    "register_platforms",
)

register_platforms()

# Fetch gcc-arm-none-eabi compiler and register for toolchain
# resolution.
load(
    "@bazel_embedded//toolchains/compilers/gcc_arm_none_eabi:gcc_arm_none_repository.bzl",
    "gcc_arm_none_compiler",
)

gcc_arm_none_compiler()

load(
    "@bazel_embedded//toolchains/gcc_arm_none_eabi:gcc_arm_none_toolchain.bzl",
    "register_gcc_arm_none_toolchain",
)

register_gcc_arm_none_toolchain()

# Rust Support
#

http_archive(
    name = "rules_rust",
    patch_args = ["-p1"],
    patches = [
        # Fix rustdoc test w/ proc macros
        # https://github.com/bazelbuild/rules_rust/pull/1952
        "//pw_rust/bazel_patches:0001-rustdoc_test-Apply-prefix-stripping-to-proc_macro-de.patch",
        # Allow `rust_repository_set` to specify `opt_level`
        # https://github.com/bazelbuild/rules_rust/pull/2036
        "//pw_rust/bazel_patches:0002-Add-opt_level-argument-to-rust_repository_set.patch",
        # Adds prototype functionality for documenting multiple crates in one
        # HTML output directory.  While the approach in this patch may have
        # issues scaling to giant mono-repos, it is apporpriate for embedded
        # projects and minimally invasive and should be easy to maintain.  Once
        # the `rules_rust` community decides on a way to propperly support this,
        # we will migrate to that solution.
        # https://github.com/konkers/rules_rust/tree/wip/rustdoc
        "//pw_rust/bazel_patches:0003-PROTOTYPE-Add-ability-to-document-multiple-crates-at.patch",
    ],
    sha256 = "190b5aeba104210f8ed9b1ff595d1f459297fe32db70f0a04f5c537a13ee0602",
    urls = ["https://github.com/bazelbuild/rules_rust/releases/download/0.24.1/rules_rust-v0.24.1.tar.gz"],
)

load("@rules_rust//rust:repositories.bzl", "rules_rust_dependencies", "rust_analyzer_toolchain_repository", "rust_repository_set")

rules_rust_dependencies()

RUST_EMBEDDED_TARGET_TRIPLES = {
    "thumbv8m.main-none-eabihf": [
        "@platforms//cpu:armv8-m",
        "@bazel_embedded//constraints/fpu:fpv5-d16",
    ],
    "thumbv7m-none-eabi": [
        "@platforms//cpu:armv7-m",
        "@bazel_embedded//constraints/fpu:none",
    ],
    "thumbv6m-none-eabi": [
        "@platforms//cpu:armv6-m",
        "@bazel_embedded//constraints/fpu:none",
    ],
}

RUST_OPT_LEVELS = {
    "thumbv8m.main-none-eabihf": {
        "dbg": "0",
        "fastbuild": "0",
        "opt": "z",
    },
    "thumbv7m-none-eabi": {
        "dbg": "0",
        "fastbuild": "0",
        "opt": "z",
    },
    "thumbv6m-none-eabi": {
        "dbg": "0",
        "fastbuild": "0",
        "opt": "z",
    },
}

# Here we register a specific set of toolchains.
#
# Note: This statement creates name mangled remotes of the form:
# `@{name}__{triplet}_tools`
# (example: `@rust_linux_x86_64__thumbv7m-none-eabi_tools/`)
rust_repository_set(
    name = "rust_linux_x86_64",
    edition = "2021",
    exec_triple = "x86_64-unknown-linux-gnu",
    extra_target_triples = RUST_EMBEDDED_TARGET_TRIPLES,
    opt_level = RUST_OPT_LEVELS,
    versions = ["1.67.0"],
)

rust_repository_set(
    name = "rust_macos_x86_64",
    edition = "2021",
    exec_triple = "x86_64-apple-darwin",
    extra_target_triples = RUST_EMBEDDED_TARGET_TRIPLES,
    opt_level = RUST_OPT_LEVELS,
    versions = ["1.67.0"],
)

# Allows creation of a `rust-project.json` file to allow rust analyzer to work.
load("@rules_rust//tools/rust_analyzer:deps.bzl", "rust_analyzer_dependencies")

# Since we do not use rust_register_toolchains, we need to define a
# rust_analyzer_toolchain.
register_toolchains(rust_analyzer_toolchain_repository(
    name = "linux_rust_analyzer_toolchain",
    exec_compatible_with = ["@platforms//os:linux"],
    # This should match the currently registered linux toolchain.
    version = "1.67.0",
))

register_toolchains(rust_analyzer_toolchain_repository(
    name = "macos_rust_analyzer_toolchain",
    exec_compatible_with = ["@platforms//os:macos"],
    # This should match the currently registered macos toolchain.
    version = "1.67.0",
))

rust_analyzer_dependencies()

# Vendored third party rust crates.
git_repository(
    name = "rust_crates",
    commit = "e4dcd91091f0537e6b5482677f2007b32a94703e",
    remote = "https://pigweed.googlesource.com/third_party/rust_crates",
    shallow_since = "1675359057 +0000",
)

# Registers platforms for use with toolchain resolution
register_execution_platforms("//pw_build/platforms:all")

load("//pw_build:target_config.bzl", "pigweed_config")

# Configure Pigweeds backend.
pigweed_config(
    name = "pigweed_config",
    build_file = "//targets:default_config.BUILD",
)

# Required by: rules_fuzzing, fuzztest
#
# Provided here explicitly to override an old version of absl that
# rules_fuzzing_dependencies attempts to pull in. That version has
# many compiler warnings on newer clang versions.
http_archive(
    name = "com_google_absl",
    sha256 = "3ea49a7d97421b88a8c48a0de16c16048e17725c7ec0f1d3ea2683a2a75adc21",
    strip_prefix = "abseil-cpp-20230125.0",
    urls = ["https://github.com/abseil/abseil-cpp/archive/refs/tags/20230125.0.tar.gz"],
)

# Set up rules for fuzz testing.
# Required by: pigweed.
# Used in modules: //pw_protobuf, //pw_tokenizer, //pw_fuzzer.
http_archive(
    name = "rules_fuzzing",
    sha256 = "d9002dd3cd6437017f08593124fdd1b13b3473c7b929ceb0e60d317cb9346118",
    strip_prefix = "rules_fuzzing-0.3.2",
    urls = ["https://github.com/bazelbuild/rules_fuzzing/archive/v0.3.2.zip"],
)

load("@rules_fuzzing//fuzzing:repositories.bzl", "rules_fuzzing_dependencies")

rules_fuzzing_dependencies()

load("@rules_fuzzing//fuzzing:init.bzl", "rules_fuzzing_init")

rules_fuzzing_init()

load("@fuzzing_py_deps//:requirements.bzl", fuzzing_install_deps = "install_deps")

fuzzing_install_deps()

# Required by: fuzztest
http_archive(
    name = "com_googlesource_code_re2",
    sha256 = "f89c61410a072e5cbcf8c27e3a778da7d6fd2f2b5b1445cd4f4508bee946ab0f",
    strip_prefix = "re2-2022-06-01",
    url = "https://github.com/google/re2/archive/refs/tags/2022-06-01.tar.gz",
)

# Required by: pigweed.
# Used in modules: //pw_fuzzer.
FUZZTEST_COMMIT = "f2e9e2a19a7b16101d1e6f01a87e639687517a1c"

http_archive(
    name = "com_google_fuzztest",
    strip_prefix = "fuzztest-" + FUZZTEST_COMMIT,
    url = "https://github.com/google/fuzztest/archive/" + FUZZTEST_COMMIT + ".zip",
)

RULES_JVM_EXTERNAL_TAG = "2.8"

RULES_JVM_EXTERNAL_SHA = "79c9850690d7614ecdb72d68394f994fef7534b292c4867ce5e7dec0aa7bdfad"

http_archive(
    name = "rules_jvm_external",
    sha256 = RULES_JVM_EXTERNAL_SHA,
    strip_prefix = "rules_jvm_external-%s" % RULES_JVM_EXTERNAL_TAG,
    url = "https://github.com/bazelbuild/rules_jvm_external/archive/%s.zip" % RULES_JVM_EXTERNAL_TAG,
)

load("@rules_jvm_external//:defs.bzl", "maven_install")

# Pull in packages for the pw_rpc Java client with Maven.
maven_install(
    artifacts = [
        "com.google.auto.value:auto-value:1.8.2",
        "com.google.auto.value:auto-value-annotations:1.8.2",
        "com.google.code.findbugs:jsr305:3.0.2",
        "com.google.flogger:flogger:0.7.1",
        "com.google.flogger:flogger-system-backend:0.7.1",
        "com.google.guava:guava:31.0.1-jre",
        "com.google.truth:truth:1.1.3",
        "org.mockito:mockito-core:4.1.0",
    ],
    repositories = [
        "https://maven.google.com/",
        "https://jcenter.bintray.com/",
        "https://repo1.maven.org/maven2",
    ],
)

new_git_repository(
    name = "micro_ecc",
    build_file = "//:third_party/micro_ecc/BUILD.micro_ecc",
    commit = "b335ee812bfcca4cd3fb0e2a436aab39553a555a",
    remote = "https://github.com/kmackay/micro-ecc.git",
    shallow_since = "1648504566 -0700",
)

git_repository(
    name = "boringssl",
    commit = "0fd67c76fc4bfb05a665c087ebfead77a3267f6d",
    remote = "https://boringssl.googlesource.com/boringssl",
    shallow_since = "1637714942 +0000",
)

git_repository(
    name = "mbedtls",
    build_file = "//:third_party/mbedtls/BUILD.mbedtls",
    # mbedtls-3.2.1 released 2022-07-12
    commit = "869298bffeea13b205343361b7a7daf2b210e33d",
    remote = "https://pigweed.googlesource.com/third_party/github/ARMmbed/mbedtls",
    shallow_since = "1648504566 -0700",
)

http_archive(
    name = "freertos",
    build_file = "//:third_party/freertos/BUILD.bazel",
    sha256 = "89af32b7568c504624f712c21fe97f7311c55fccb7ae6163cda7adde1cde7f62",
    strip_prefix = "FreeRTOS-Kernel-10.5.1",
    urls = ["https://github.com/FreeRTOS/FreeRTOS-Kernel/archive/refs/tags/V10.5.1.tar.gz"],
)
