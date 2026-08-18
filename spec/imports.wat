;; Canonical Core WebAssembly import declarations for WPSI 0.1.
;;
;; This module is declarative documentation: consumers import only the WPSI
;; functions they actually require.

(module
  ;; Representative concrete result types for host-allocated strings.
  ;; Allocating string imports are templates: an importing module supplies its
  ;; own concrete array type with the matching element storage class.
  (type $wpsi_string_i8 (array (mut i8)))
  (type $wpsi_string_i16 (array (mut i16)))
  (type $wpsi_string_i32 (array (mut i32)))

  ;; Core
  (import "facet" "abi_version" (func $abi_version (result i32)))
  (import "facet" "handle_close" (func $handle_close (param i32) (result i32)))
  (import "facet" "proc_exit" (func $proc_exit (param i32)))
  (import "facet" "proc_yield" (func $proc_yield (result i32)))
  (import "facet" "stdio_stdin" (func $stdio_stdin (result i32 i32)))
  (import "facet" "stdio_stdout" (func $stdio_stdout (result i32 i32)))
  (import "facet" "stdio_stderr" (func $stdio_stderr (result i32 i32)))

  ;; Arguments and environment
  (import "facet" "args_count" (func $args_count (result i32 i32)))
  (import "facet" "args_len_i8" (func $args_len_i8 (param i32 i32) (result i64 i32)))
  (import "facet" "args_len_i16" (func $args_len_i16 (param i32 i32) (result i64 i32)))
  (import "facet" "args_len_i32" (func $args_len_i32 (param i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem32_i8" (func $args_read_mem32_i8 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem32_i16" (func $args_read_mem32_i16 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem32_i32" (func $args_read_mem32_i32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem64_i8" (func $args_read_mem64_i8 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "args_read_mem64_i16" (func $args_read_mem64_i16 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "args_read_mem64_i32" (func $args_read_mem64_i32 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "args_read_into_array_i8" (func $args_read_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "args_read_into_array_i16" (func $args_read_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "args_read_into_array_i32" (func $args_read_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "args_read_array_i8" (func $args_read_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "facet" "args_read_array_i16" (func $args_read_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "facet" "args_read_array_i32" (func $args_read_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32)))

  (import "facet" "env_count" (func $env_count (result i32 i32)))
  (import "facet" "env_len_i8" (func $env_len_i8 (param i32 i32 i32) (result i64 i32)))
  (import "facet" "env_len_i16" (func $env_len_i16 (param i32 i32 i32) (result i64 i32)))
  (import "facet" "env_len_i32" (func $env_len_i32 (param i32 i32 i32) (result i64 i32)))
  (import "facet" "env_read_mem32_i8" (func $env_read_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "env_read_mem32_i16" (func $env_read_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "env_read_mem32_i32" (func $env_read_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "env_read_mem64_i8" (func $env_read_mem64_i8 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "env_read_mem64_i16" (func $env_read_mem64_i16 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "env_read_mem64_i32" (func $env_read_mem64_i32 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "env_read_into_array_i8" (func $env_read_into_array_i8 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "env_read_into_array_i16" (func $env_read_into_array_i16 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "env_read_into_array_i32" (func $env_read_into_array_i32 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "env_read_array_i8" (func $env_read_array_i8 (param i32 i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "facet" "env_read_array_i16" (func $env_read_array_i16 (param i32 i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "facet" "env_read_array_i32" (func $env_read_array_i32 (param i32 i32 i32) (result (ref null $wpsi_string_i32) i32)))

  ;; Clocks
  (import "facet" "clock_system_now"
    (func $clock_system_now (result i64 i32 i32)))
  (import "facet" "clock_monotonic_now"
    (func $clock_monotonic_now (result i64 i32)))
  (import "facet" "clock_monotonic_resolution"
    (func $clock_monotonic_resolution (result i64 i32)))
  (import "facet" "sleep_for" (func $sleep_for (param i64) (result i32)))
  (import "facet" "sleep_until" (func $sleep_until (param i64) (result i32)))

  ;; Randomness
  (import "facet" "random_u64" (func $random_u64 (result i64 i32)))
  (import "facet" "random_fill_mem32"
    (func $random_fill_mem32 (param i32 i32 i32) (result i64 i32)))
  (import "facet" "random_fill_mem64"
    (func $random_fill_mem64 (param i32 i64 i64) (result i64 i32)))
  (import "facet" "random_fill_array_i8"
    (func $random_fill_array_i8 (param (ref array) i64 i64) (result i64 i32)))
  (import "facet" "random_fill_array_i16"
    (func $random_fill_array_i16 (param (ref array) i64 i64) (result i64 i32)))
  (import "facet" "random_fill_array_i32"
    (func $random_fill_array_i32 (param (ref array) i64 i64) (result i64 i32)))
  (import "facet" "random_fill_array_i64"
    (func $random_fill_array_i64 (param (ref array) i64 i64) (result i64 i32)))
  (import "facet" "random_fill_array_v128"
    (func $random_fill_array_v128 (param (ref array) i64 i64) (result i64 i32)))

  ;; Filesystem preopens
  (import "facet" "fs_preopen_count" (func $fs_preopen_count (result i32 i32)))
  (import "facet" "fs_preopen_get" (func $fs_preopen_get (param i32) (result i32 i32)))
  (import "facet" "fs_preopen_name_len_i8" (func $fs_preopen_name_len_i8 (param i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_len_i16" (func $fs_preopen_name_len_i16 (param i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_len_i32" (func $fs_preopen_name_len_i32 (param i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem32_i8" (func $fs_preopen_name_read_mem32_i8 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem32_i16" (func $fs_preopen_name_read_mem32_i16 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem32_i32" (func $fs_preopen_name_read_mem32_i32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem64_i8" (func $fs_preopen_name_read_mem64_i8 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem64_i16" (func $fs_preopen_name_read_mem64_i16 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem64_i32" (func $fs_preopen_name_read_mem64_i32 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_into_array_i8" (func $fs_preopen_name_read_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_into_array_i16" (func $fs_preopen_name_read_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_into_array_i32" (func $fs_preopen_name_read_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_array_i8" (func $fs_preopen_name_read_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "facet" "fs_preopen_name_read_array_i16" (func $fs_preopen_name_read_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "facet" "fs_preopen_name_read_array_i32" (func $fs_preopen_name_read_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32)))

  ;; Descriptor metadata
  (import "facet" "fd_rights" (func $fd_rights (param i32) (result i64 i32)))
  (import "facet" "fd_get_flags" (func $fd_get_flags (param i32) (result i32 i32)))
  (import "facet" "fd_set_flags" (func $fd_set_flags (param i32 i32) (result i32)))
  (import "facet" "fd_stat"
    (func $fd_stat
      (param i32)
      (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))

  ;; Sequential reads
  (import "facet" "fd_read_mem32"
    (func $fd_read_mem32 (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_read_mem64"
    (func $fd_read_mem64 (param i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_read_array_i8"
    (func $fd_read_array_i8 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_read_array_i16"
    (func $fd_read_array_i16 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_read_array_i32"
    (func $fd_read_array_i32 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_read_array_i64"
    (func $fd_read_array_i64 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_read_array_v128"
    (func $fd_read_array_v128 (param i32 (ref array) i64 i64) (result i64 i32)))

  ;; Sequential writes
  (import "facet" "fd_write_mem32"
    (func $fd_write_mem32 (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_write_mem64"
    (func $fd_write_mem64 (param i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_write_array_i8"
    (func $fd_write_array_i8 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_write_array_i16"
    (func $fd_write_array_i16 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_write_array_i32"
    (func $fd_write_array_i32 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_write_array_i64"
    (func $fd_write_array_i64 (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_write_array_v128"
    (func $fd_write_array_v128 (param i32 (ref array) i64 i64) (result i64 i32)))

  ;; Positional reads
  (import "facet" "fd_pread_mem32"
    (func $fd_pread_mem32 (param i32 i64 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_pread_mem64"
    (func $fd_pread_mem64 (param i32 i64 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_pread_array_i8"
    (func $fd_pread_array_i8 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pread_array_i16"
    (func $fd_pread_array_i16 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pread_array_i32"
    (func $fd_pread_array_i32 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pread_array_i64"
    (func $fd_pread_array_i64 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pread_array_v128"
    (func $fd_pread_array_v128 (param i32 i64 (ref array) i64 i64) (result i64 i32)))

  ;; Positional writes
  (import "facet" "fd_pwrite_mem32"
    (func $fd_pwrite_mem32 (param i32 i64 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_pwrite_mem64"
    (func $fd_pwrite_mem64 (param i32 i64 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_pwrite_array_i8"
    (func $fd_pwrite_array_i8 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pwrite_array_i16"
    (func $fd_pwrite_array_i16 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pwrite_array_i32"
    (func $fd_pwrite_array_i32 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pwrite_array_i64"
    (func $fd_pwrite_array_i64 (param i32 i64 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_pwrite_array_v128"
    (func $fd_pwrite_array_v128 (param i32 i64 (ref array) i64 i64) (result i64 i32)))

  ;; Scatter/gather
  (import "facet" "fd_readv_mem32"
    (func $fd_readv_mem32 (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_mem32"
    (func $fd_writev_mem32 (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_readv_mem64"
    (func $fd_readv_mem64 (param i32 i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_writev_mem64"
    (func $fd_writev_mem64 (param i32 i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_readv_array_i8"
    (func $fd_readv_array_i8 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_readv_array_i16"
    (func $fd_readv_array_i16 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_readv_array_i32"
    (func $fd_readv_array_i32 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_readv_array_i64"
    (func $fd_readv_array_i64 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_readv_array_v128"
    (func $fd_readv_array_v128 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_array_i8"
    (func $fd_writev_array_i8 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_array_i16"
    (func $fd_writev_array_i16 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_array_i32"
    (func $fd_writev_array_i32 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_array_i64"
    (func $fd_writev_array_i64 (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_array_v128"
    (func $fd_writev_array_v128 (param i32 (ref array) i32 i32) (result i64 i32)))

  ;; Positioning and persistence
  (import "facet" "fd_seek" (func $fd_seek (param i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_tell" (func $fd_tell (param i32) (result i64 i32)))
  (import "facet" "fd_set_size" (func $fd_set_size (param i32 i64) (result i32)))
  (import "facet" "fd_sync" (func $fd_sync (param i32) (result i32)))
  (import "facet" "fd_datasync" (func $fd_datasync (param i32) (result i32)))

  ;; Textual filesystem paths
  (import "facet" "path_open_mem32_i8" (func $path_open_mem32_i8 (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_mem64_i8" (func $path_open_mem64_i8 (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_array_i8" (func $path_open_array_i8 (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_stat_mem32_i8" (func $path_stat_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_mem64_i8" (func $path_stat_mem64_i8 (param i32 i32 i64 i64 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_array_i8" (func $path_stat_array_i8 (param i32 (ref array) i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_create_dir_mem32_i8" (func $path_create_dir_mem32_i8 (param i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_create_dir_mem64_i8" (func $path_create_dir_mem64_i8 (param i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_create_dir_array_i8" (func $path_create_dir_array_i8 (param i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem32_i8" (func $path_remove_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem64_i8" (func $path_remove_mem64_i8 (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_remove_array_i8" (func $path_remove_array_i8 (param i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem32_i8" (func $path_rename_mem32_i8 (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem64_i8" (func $path_rename_mem64_i8 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_rename_array_i8" (func $path_rename_array_i8 (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_open_mem32_i16" (func $path_open_mem32_i16 (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_mem64_i16" (func $path_open_mem64_i16 (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_array_i16" (func $path_open_array_i16 (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_stat_mem32_i16" (func $path_stat_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_mem64_i16" (func $path_stat_mem64_i16 (param i32 i32 i64 i64 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_array_i16" (func $path_stat_array_i16 (param i32 (ref array) i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_create_dir_mem32_i16" (func $path_create_dir_mem32_i16 (param i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_create_dir_mem64_i16" (func $path_create_dir_mem64_i16 (param i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_create_dir_array_i16" (func $path_create_dir_array_i16 (param i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem32_i16" (func $path_remove_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem64_i16" (func $path_remove_mem64_i16 (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_remove_array_i16" (func $path_remove_array_i16 (param i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem32_i16" (func $path_rename_mem32_i16 (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem64_i16" (func $path_rename_mem64_i16 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_rename_array_i16" (func $path_rename_array_i16 (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_open_mem32_i32" (func $path_open_mem32_i32 (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_mem64_i32" (func $path_open_mem64_i32 (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_array_i32" (func $path_open_array_i32 (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_stat_mem32_i32" (func $path_stat_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_mem64_i32" (func $path_stat_mem64_i32 (param i32 i32 i64 i64 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_array_i32" (func $path_stat_array_i32 (param i32 (ref array) i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_create_dir_mem32_i32" (func $path_create_dir_mem32_i32 (param i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_create_dir_mem64_i32" (func $path_create_dir_mem64_i32 (param i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_create_dir_array_i32" (func $path_create_dir_array_i32 (param i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem32_i32" (func $path_remove_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem64_i32" (func $path_remove_mem64_i32 (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_remove_array_i32" (func $path_remove_array_i32 (param i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem32_i32" (func $path_rename_mem32_i32 (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem64_i32" (func $path_rename_mem64_i32 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_rename_array_i32" (func $path_rename_array_i32 (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))

  ;; Directory iteration
  (import "facet" "dir_iter_open" (func $dir_iter_open (param i32) (result i32 i32)))
  (import "facet" "dir_iter_next_len_i8" (func $dir_iter_next_len_i8 (param i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_mem32_i8" (func $dir_iter_next_mem32_i8 (param i32 i32 i32 i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_mem64_i8" (func $dir_iter_next_mem64_i8 (param i32 i32 i32 i64 i64) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_into_array_i8" (func $dir_iter_next_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_array_i8" (func $dir_iter_next_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_len_i16" (func $dir_iter_next_len_i16 (param i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_mem32_i16" (func $dir_iter_next_mem32_i16 (param i32 i32 i32 i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_mem64_i16" (func $dir_iter_next_mem64_i16 (param i32 i32 i32 i64 i64) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_into_array_i16" (func $dir_iter_next_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_array_i16" (func $dir_iter_next_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_len_i32" (func $dir_iter_next_len_i32 (param i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_mem32_i32" (func $dir_iter_next_mem32_i32 (param i32 i32 i32 i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_mem64_i32" (func $dir_iter_next_mem64_i32 (param i32 i32 i32 i64 i64) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_into_array_i32" (func $dir_iter_next_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32 i64 i32 i32)))
  (import "facet" "dir_iter_next_array_i32" (func $dir_iter_next_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32 i64 i32 i32)))
  (import "facet" "dir_iter_rewind" (func $dir_iter_rewind (param i32) (result i32)))

  ;; Links and symbolic links
  (import "facet" "path_link_mem32_i8" (func $path_link_mem32_i8 (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_link_mem64_i8" (func $path_link_mem64_i8 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_link_array_i8" (func $path_link_array_i8 (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem32_i8" (func $path_symlink_mem32_i8 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem64_i8" (func $path_symlink_mem64_i8 (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_symlink_array_i8" (func $path_symlink_array_i8 (param (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_mem32_i8" (func $path_readlink_len_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem32_i8" (func $path_readlink_mem32_i8 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_mem64_i8" (func $path_readlink_len_mem64_i8 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem64_i8" (func $path_readlink_mem64_i8 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_array_i8" (func $path_readlink_len_array_i8 (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_into_array_i8" (func $path_readlink_into_array_i8 (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_array_i8" (func $path_readlink_array_i8 (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "facet" "path_link_mem32_i16" (func $path_link_mem32_i16 (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_link_mem64_i16" (func $path_link_mem64_i16 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_link_array_i16" (func $path_link_array_i16 (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem32_i16" (func $path_symlink_mem32_i16 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem64_i16" (func $path_symlink_mem64_i16 (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_symlink_array_i16" (func $path_symlink_array_i16 (param (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_mem32_i16" (func $path_readlink_len_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem32_i16" (func $path_readlink_mem32_i16 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_mem64_i16" (func $path_readlink_len_mem64_i16 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem64_i16" (func $path_readlink_mem64_i16 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_array_i16" (func $path_readlink_len_array_i16 (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_into_array_i16" (func $path_readlink_into_array_i16 (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_array_i16" (func $path_readlink_array_i16 (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "facet" "path_link_mem32_i32" (func $path_link_mem32_i32 (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_link_mem64_i32" (func $path_link_mem64_i32 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_link_array_i32" (func $path_link_array_i32 (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem32_i32" (func $path_symlink_mem32_i32 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem64_i32" (func $path_symlink_mem64_i32 (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_symlink_array_i32" (func $path_symlink_array_i32 (param (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_mem32_i32" (func $path_readlink_len_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem32_i32" (func $path_readlink_mem32_i32 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_mem64_i32" (func $path_readlink_len_mem64_i32 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem64_i32" (func $path_readlink_mem64_i32 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_array_i32" (func $path_readlink_len_array_i32 (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_into_array_i32" (func $path_readlink_into_array_i32 (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_array_i32" (func $path_readlink_array_i32 (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_i32) i32)))

  ;; Socket lifecycle
  (import "facet" "socket_open"
    (func $socket_open (param i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "socket_bind"
    (func $socket_bind (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "socket_connect"
    (func $socket_connect (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "socket_listen"
    (func $socket_listen (param i32 i32) (result i32)))
  (import "facet" "socket_accept"
    (func $socket_accept
      (param i32 i32)
      (result i32 i32 i64 i64 i32 i32 i32)))
  (import "facet" "socket_local_address"
    (func $socket_local_address
      (param i32)
      (result i32 i64 i64 i32 i32 i32)))
  (import "facet" "socket_peer_address"
    (func $socket_peer_address
      (param i32)
      (result i32 i64 i64 i32 i32 i32)))
  (import "facet" "socket_shutdown"
    (func $socket_shutdown (param i32 i32) (result i32)))

  ;; Datagram receive
  (import "facet" "socket_recvfrom_mem32"
    (func $socket_recvfrom_mem32
      (param i32 i32 i32 i32 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_mem64"
    (func $socket_recvfrom_mem64
      (param i32 i32 i64 i64 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i8"
    (func $socket_recvfrom_array_i8
      (param i32 (ref array) i64 i64 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i16"
    (func $socket_recvfrom_array_i16
      (param i32 (ref array) i64 i64 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i32"
    (func $socket_recvfrom_array_i32
      (param i32 (ref array) i64 i64 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i64"
    (func $socket_recvfrom_array_i64
      (param i32 (ref array) i64 i64 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_v128"
    (func $socket_recvfrom_array_v128
      (param i32 (ref array) i64 i64 i32)
      (result i64 i32 i64 i64 i32 i32 i32 i32)))

  ;; Datagram send
  (import "facet" "socket_sendto_mem32"
    (func $socket_sendto_mem32
      (param i32 i32 i32 i32 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))
  (import "facet" "socket_sendto_mem64"
    (func $socket_sendto_mem64
      (param i32 i32 i64 i64 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))
  (import "facet" "socket_sendto_array_i8"
    (func $socket_sendto_array_i8
      (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))
  (import "facet" "socket_sendto_array_i16"
    (func $socket_sendto_array_i16
      (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))
  (import "facet" "socket_sendto_array_i32"
    (func $socket_sendto_array_i32
      (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))
  (import "facet" "socket_sendto_array_i64"
    (func $socket_sendto_array_i64
      (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))
  (import "facet" "socket_sendto_array_v128"
    (func $socket_sendto_array_v128
      (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
      (result i64 i32)))

  ;; DNS
  (import "facet" "dns_resolve_mem32_i8" (func $dns_resolve_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem64_i8" (func $dns_resolve_mem64_i8 (param i32 i64 i64 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_array_i8" (func $dns_resolve_array_i8 (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem32_i16" (func $dns_resolve_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem64_i16" (func $dns_resolve_mem64_i16 (param i32 i64 i64 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_array_i16" (func $dns_resolve_array_i16 (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem32_i32" (func $dns_resolve_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem64_i32" (func $dns_resolve_mem64_i32 (param i32 i64 i64 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_array_i32" (func $dns_resolve_array_i32 (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_next"
    (func $dns_next (param i32) (result i32 i64 i64 i32 i32 i32)))

  ;; Polling
  (import "facet" "poll_create" (func $poll_create (result i32 i32)))
  (import "facet" "poll_add_fd"
    (func $poll_add_fd (param i32 i32 i32 i64) (result i32)))
  (import "facet" "poll_update_fd"
    (func $poll_update_fd (param i32 i32 i32 i64) (result i32)))
  (import "facet" "poll_remove_fd"
    (func $poll_remove_fd (param i32 i32) (result i32)))
  (import "facet" "poll_add_timer"
    (func $poll_add_timer (param i32 i64 i64) (result i32 i32)))
  (import "facet" "poll_remove_timer"
    (func $poll_remove_timer (param i32 i32) (result i32)))
  (import "facet" "poll_wait"
    (func $poll_wait (param i32 i64) (result i32 i32)))
  (import "facet" "poll_next"
    (func $poll_next (param i32) (result i32 i32 i32 i64 i32 i32)))
)
