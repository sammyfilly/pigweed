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

include($ENV{PW_ROOT}/pw_build/pigweed.cmake)

if(NOT CONFIG_PIGWEED_INTERRUPT_CONTEXT)
  return()
endif()

pw_add_library(pw_interrupt_zephyr.context INTERFACE
  HEADERS
    public/pw_interrupt_zephyr/context_inline.h
    public_overrides/pw_interrupt_backend/context_inline.h
  PUBLIC_INCLUDES
    public
    public_overrides
  PUBLIC_DEPS
    pw_interrupt.context.facade
)
pw_zephyrize_libraries_ifdef(CONFIG_PIGWEED_INTERRUPT_CONTEXT pw_interrupt_zephyr.context)
