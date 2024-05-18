# 0 "chapter_8/exercise_8_04/syscalls.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 0 "<command-line>" 2
# 1 "chapter_8/exercise_8_04/syscalls.c"
# 1 "/usr/include/fcntl.h" 1 3 4
# 25 "/usr/include/fcntl.h" 3 4
# 1 "/usr/include/features.h" 1 3 4
# 392 "/usr/include/features.h" 3 4
# 1 "/usr/include/features-time64.h" 1 3 4
# 20 "/usr/include/features-time64.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/wordsize.h" 1 3 4
# 21 "/usr/include/features-time64.h" 2 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/timesize.h" 1 3 4
# 19 "/usr/include/x86_64-linux-gnu/bits/timesize.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/wordsize.h" 1 3 4
# 20 "/usr/include/x86_64-linux-gnu/bits/timesize.h" 2 3 4
# 22 "/usr/include/features-time64.h" 2 3 4
# 393 "/usr/include/features.h" 2 3 4
# 486 "/usr/include/features.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/sys/cdefs.h" 1 3 4
# 559 "/usr/include/x86_64-linux-gnu/sys/cdefs.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/wordsize.h" 1 3 4
# 560 "/usr/include/x86_64-linux-gnu/sys/cdefs.h" 2 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/long-double.h" 1 3 4
# 561 "/usr/include/x86_64-linux-gnu/sys/cdefs.h" 2 3 4
# 487 "/usr/include/features.h" 2 3 4
# 510 "/usr/include/features.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/gnu/stubs.h" 1 3 4
# 10 "/usr/include/x86_64-linux-gnu/gnu/stubs.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/gnu/stubs-64.h" 1 3 4
# 11 "/usr/include/x86_64-linux-gnu/gnu/stubs.h" 2 3 4
# 511 "/usr/include/features.h" 2 3 4
# 26 "/usr/include/fcntl.h" 2 3 4





# 1 "/usr/include/x86_64-linux-gnu/bits/types.h" 1 3 4
# 27 "/usr/include/x86_64-linux-gnu/bits/types.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/wordsize.h" 1 3 4
# 28 "/usr/include/x86_64-linux-gnu/bits/types.h" 2 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/timesize.h" 1 3 4
# 19 "/usr/include/x86_64-linux-gnu/bits/timesize.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/wordsize.h" 1 3 4
# 20 "/usr/include/x86_64-linux-gnu/bits/timesize.h" 2 3 4
# 29 "/usr/include/x86_64-linux-gnu/bits/types.h" 2 3 4



# 31 "/usr/include/x86_64-linux-gnu/bits/types.h" 3 4
typedef unsigned char __u_char;
typedef unsigned short int __u_short;
typedef unsigned int __u_int;
typedef unsigned long int __u_long;


typedef signed char __int8_t;
typedef unsigned char __uint8_t;
typedef signed short int __int16_t;
typedef unsigned short int __uint16_t;
typedef signed int __int32_t;
typedef unsigned int __uint32_t;

typedef signed long int __int64_t;
typedef unsigned long int __uint64_t;






typedef __int8_t __int_least8_t;
typedef __uint8_t __uint_least8_t;
typedef __int16_t __int_least16_t;
typedef __uint16_t __uint_least16_t;
typedef __int32_t __int_least32_t;
typedef __uint32_t __uint_least32_t;
typedef __int64_t __int_least64_t;
typedef __uint64_t __uint_least64_t;



typedef long int __quad_t;
typedef unsigned long int __u_quad_t;







typedef long int __intmax_t;
typedef unsigned long int __uintmax_t;
# 141 "/usr/include/x86_64-linux-gnu/bits/types.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/typesizes.h" 1 3 4
# 142 "/usr/include/x86_64-linux-gnu/bits/types.h" 2 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/time64.h" 1 3 4
# 143 "/usr/include/x86_64-linux-gnu/bits/types.h" 2 3 4


typedef unsigned long int __dev_t;
typedef unsigned int __uid_t;
typedef unsigned int __gid_t;
typedef unsigned long int __ino_t;
typedef unsigned long int __ino64_t;
typedef unsigned int __mode_t;
typedef unsigned long int __nlink_t;
typedef long int __off_t;
typedef long int __off64_t;
typedef int __pid_t;
typedef struct { int __val[2]; } __fsid_t;
typedef long int __clock_t;
typedef unsigned long int __rlim_t;
typedef unsigned long int __rlim64_t;
typedef unsigned int __id_t;
typedef long int __time_t;
typedef unsigned int __useconds_t;
typedef long int __suseconds_t;
typedef long int __suseconds64_t;

typedef int __daddr_t;
typedef int __key_t;


typedef int __clockid_t;


typedef void * __timer_t;


typedef long int __blksize_t;




typedef long int __blkcnt_t;
typedef long int __blkcnt64_t;


typedef unsigned long int __fsblkcnt_t;
typedef unsigned long int __fsblkcnt64_t;


typedef unsigned long int __fsfilcnt_t;
typedef unsigned long int __fsfilcnt64_t;


typedef long int __fsword_t;

typedef long int __ssize_t;


typedef long int __syscall_slong_t;

typedef unsigned long int __syscall_ulong_t;



typedef __off64_t __loff_t;
typedef char *__caddr_t;


typedef long int __intptr_t;


typedef unsigned int __socklen_t;




typedef int __sig_atomic_t;
# 32 "/usr/include/fcntl.h" 2 3 4



# 1 "/usr/include/x86_64-linux-gnu/bits/fcntl.h" 1 3 4
# 35 "/usr/include/x86_64-linux-gnu/bits/fcntl.h" 3 4
struct flock
  {
    short int l_type;
    short int l_whence;

    __off_t l_start;
    __off_t l_len;




    __pid_t l_pid;
  };
# 61 "/usr/include/x86_64-linux-gnu/bits/fcntl.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/fcntl-linux.h" 1 3 4
# 393 "/usr/include/x86_64-linux-gnu/bits/fcntl-linux.h" 3 4

# 467 "/usr/include/x86_64-linux-gnu/bits/fcntl-linux.h" 3 4

# 62 "/usr/include/x86_64-linux-gnu/bits/fcntl.h" 2 3 4
# 36 "/usr/include/fcntl.h" 2 3 4
# 50 "/usr/include/fcntl.h" 3 4
typedef __mode_t mode_t;





typedef __off_t off_t;
# 69 "/usr/include/fcntl.h" 3 4
typedef __pid_t pid_t;





# 1 "/usr/include/x86_64-linux-gnu/bits/types/struct_timespec.h" 1 3 4





# 1 "/usr/include/x86_64-linux-gnu/bits/endian.h" 1 3 4
# 35 "/usr/include/x86_64-linux-gnu/bits/endian.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/endianness.h" 1 3 4
# 36 "/usr/include/x86_64-linux-gnu/bits/endian.h" 2 3 4
# 7 "/usr/include/x86_64-linux-gnu/bits/types/struct_timespec.h" 2 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/types/time_t.h" 1 3 4
# 10 "/usr/include/x86_64-linux-gnu/bits/types/time_t.h" 3 4
typedef __time_t time_t;
# 8 "/usr/include/x86_64-linux-gnu/bits/types/struct_timespec.h" 2 3 4



struct timespec
{



  __time_t tv_sec;




  __syscall_slong_t tv_nsec;
# 31 "/usr/include/x86_64-linux-gnu/bits/types/struct_timespec.h" 3 4
};
# 76 "/usr/include/fcntl.h" 2 3 4


# 1 "/usr/include/x86_64-linux-gnu/bits/stat.h" 1 3 4
# 25 "/usr/include/x86_64-linux-gnu/bits/stat.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/struct_stat.h" 1 3 4
# 26 "/usr/include/x86_64-linux-gnu/bits/struct_stat.h" 3 4
struct stat
  {



    __dev_t st_dev;




    __ino_t st_ino;







    __nlink_t st_nlink;
    __mode_t st_mode;

    __uid_t st_uid;
    __gid_t st_gid;

    int __pad0;

    __dev_t st_rdev;




    __off_t st_size;



    __blksize_t st_blksize;

    __blkcnt_t st_blocks;
# 74 "/usr/include/x86_64-linux-gnu/bits/struct_stat.h" 3 4
    struct timespec st_atim;
    struct timespec st_mtim;
    struct timespec st_ctim;
# 89 "/usr/include/x86_64-linux-gnu/bits/struct_stat.h" 3 4
    __syscall_slong_t __glibc_reserved[3];
# 99 "/usr/include/x86_64-linux-gnu/bits/struct_stat.h" 3 4
  };
# 26 "/usr/include/x86_64-linux-gnu/bits/stat.h" 2 3 4
# 79 "/usr/include/fcntl.h" 2 3 4
# 149 "/usr/include/fcntl.h" 3 4
extern int fcntl (int __fd, int __cmd, ...);
# 181 "/usr/include/fcntl.h" 3 4
extern int open (const char *__file, int __oflag, ...) __attribute__ ((__nonnull__ (1)));
# 205 "/usr/include/fcntl.h" 3 4
extern int openat (int __fd, const char *__file, int __oflag, ...)
     __attribute__ ((__nonnull__ (2)));
# 227 "/usr/include/fcntl.h" 3 4
extern int creat (const char *__file, mode_t __mode) __attribute__ ((__nonnull__ (1)));
# 256 "/usr/include/fcntl.h" 3 4
extern int lockf (int __fd, int __cmd, off_t __len);
# 273 "/usr/include/fcntl.h" 3 4
extern int posix_fadvise (int __fd, off_t __offset, off_t __len,
     int __advise) __attribute__ ((__nothrow__ , __leaf__));
# 295 "/usr/include/fcntl.h" 3 4
extern int posix_fallocate (int __fd, off_t __offset, off_t __len);
# 317 "/usr/include/fcntl.h" 3 4

# 2 "chapter_8/exercise_8_04/syscalls.c" 2
# 1 "chapter_8/exercise_8_04/syscalls.h" 1
# 14 "chapter_8/exercise_8_04/syscalls.h"

# 14 "chapter_8/exercise_8_04/syscalls.h"
struct _io_buffer_file
{
  int counter;
  char *next_char_pos_p;
  char *base;
  struct
  {
    int _READ : 1;
    int _WRITE : 1;
    int _UNBUF : 1;
    int _EOF : 1;
    int _ERR : 1;
  } flag;
  int file_descriptor;
};

typedef struct _io_buffer_file FILE;

extern FILE _io_buffer[20];

int _fill_buffer(FILE *);
int _flush_buffer(int c, FILE *file_p);
int file_flush(FILE *file_p);
FILE *file_open(char *name, char *mode);
int file_close(FILE *file_p);
int file_seek(FILE *file_p, long offset, int whence);
# 3 "chapter_8/exercise_8_04/syscalls.c" 2



FILE _io_buffer[20] = {
    {0, (char *)0, (char *)0, {1, 0, 0, 0, 0}, 0},
    {0, (char *)0, (char *)0, {0, 1, 0, 0, 0}, 1},
    {0, (char *)0, (char *)0, {0, 1, 1, 0, 0}, 2}
};

void free(void *ptr);
void *malloc(long unsigned int size);
long int lseek(int file_descriptor, long int offset, int whence);
long int read(int file_descriptor, void *buffer, long unsigned int nr_of_bytes);
long int write(int file_descriptor, void *buffer, long unsigned int nr_of_bytes);
int close(int file_descriptor);

int _fill_buffer(FILE *file_p)
{
  int buffer_size;

  if (file_p->flag._READ == 0 || file_p->flag._EOF == 1 || file_p->flag._ERR == 1)
  {
    return (-1);
  }

  buffer_size = (file_p->flag._UNBUF == 1) ? 1 : 1024;

  if (file_p->base == 0)
  {
    if ((file_p->base = (char *)malloc(buffer_size)) == 0)
    {
      return (-1);
    }
  }

  file_p->next_char_pos_p = file_p->base;
  file_p->counter = read(file_p->file_descriptor, file_p->next_char_pos_p, buffer_size);

  if (--file_p->counter < 0)
  {
    if (file_p->counter == -1)
    {
      file_p->flag._EOF = 1;
    }
    else
    {
      file_p->flag._ERR = 1;
    }

    file_p->counter = 0;
    return (-1);
  }

  return (unsigned char)*file_p->next_char_pos_p++;
}

int _flush_buffer(int c, FILE *file_p)
{
  int buffer_size;

  if (file_p->flag._WRITE == 0 || file_p->flag._ERR == 1)
  {
    return (-1);
  }

  buffer_size = (file_p->flag._UNBUF == 1) ? 1 : 1024;

  if (file_p->base == 0)
  {
    if ((file_p->base = (char *)malloc(buffer_size)) == 0)
    {
      return (-1);
    }
  }
  else
  {
    unsigned long nr_of_bytes = file_p->next_char_pos_p - file_p->base;
    if ((write(file_p->file_descriptor, file_p->base, nr_of_bytes)) != nr_of_bytes)
    {
      file_p->flag._ERR = 1;
      return (-1);
    }
  }

  file_p->next_char_pos_p = file_p->base;
  *file_p->next_char_pos_p++ = c;
  file_p->counter = buffer_size - 1;

  return c;
}

int file_flush(FILE *file_p)
{
  if (file_p->flag._WRITE == 0)
  {
    file_p->flag._ERR = 1;
    return (-1);
  }

  if (_flush_buffer('0', file_p) == (-1))
  {
    return (-1);
  }

  file_p->next_char_pos_p = file_p->base;
  file_p->counter = (file_p->flag._UNBUF == 1) ? 1 : 1024;

  return 0;
}

FILE *file_open(char *name, char *mode)
{
  int file_descriptor;
  FILE *file_p;

  if (*mode != 'r' && *mode != 'w' && *mode != 'a')
  {
    return 0;
  }

  for (file_p = _io_buffer; file_p < _io_buffer + 20; ++file_p)
  {
    if (file_p->flag._READ == 0 && file_p->flag._WRITE == 0)
    {
      break;
    }
  }

  if (file_p >= _io_buffer + 20)
  {
    return 0;
  }

  if (*mode == 'w')
  {
    file_descriptor = creat(name, 0666);
  }
  else if (*mode == 'a')
  {
    if ((file_descriptor = open(name, 
# 142 "chapter_8/exercise_8_04/syscalls.c" 3 4
                                     01
# 142 "chapter_8/exercise_8_04/syscalls.c"
                                             , 0)) == -1)
    {
      file_descriptor = creat(name, 0666);
    }
    lseek(file_descriptor, 0L, 2);
  }
  else
  {
    file_descriptor = open(name, 
# 150 "chapter_8/exercise_8_04/syscalls.c" 3 4
                                00
# 150 "chapter_8/exercise_8_04/syscalls.c"
                                        , 0);
  }

  if (file_descriptor == -1)
  {
    return 0;
  }

  file_p->file_descriptor = file_descriptor;
  file_p->counter = 0;
  file_p->base = 0;
  file_p->flag._EOF = 0;
  file_p->flag._ERR = 0;
  file_p->flag._READ = (*mode == 'r') ? 1 : 0;
  file_p->flag._WRITE = (*mode == 'r') ? 0 : 1;

  return file_p;
}

int file_close(FILE *file_p)
{
  if (file_flush(file_p) == (-1))
  {
    return (-1);
  }

  free(file_p->base);
  file_p->next_char_pos_p = 0;
  file_p->base = 0;
  file_p->counter = 0;
  close(file_p->file_descriptor);

  return 0;
}

int file_seek(FILE *file_p, long offset, int whence)
{
  if (file_p->flag._UNBUF == 0)
  {
    if (file_p->flag._READ == 1)
    {
      file_p->counter = 0;
      file_p->next_char_pos_p = file_p->base;
    }
    else if (file_p->flag._WRITE == 1)
    {
      file_flush(file_p);
    }
  }

  return (lseek(file_p->file_descriptor, offset, whence) < 0);
}

int main(void)
{
  FILE *file_in_p;
  FILE *file_out_p;

  if ((file_in_p = file_open("syscalls.c", "r")) == 0)
  {
    write(1, "Error: could not open the file.\n", 33);
    return 1;
  }

  if ((file_out_p = file_open("out.txt", "w")) == 0)
  {
    write(1, "Error: could not open the file.\n", 33);
    return 1;
  }

  if (file_seek(file_in_p, 5, 0) == -1)
  {
    return 1;
  }

  char c;
  while ((c = ((--file_in_p->counter >= 0) ? (unsigned char)*(file_in_p)->next_char_pos_p++ : _fill_buffer(file_in_p))) != (-1))
  {
    ((--file_out_p->counter >= 0) ? *file_out_p->next_char_pos_p++ = c : _flush_buffer(c, file_out_p));
  }
  file_close(file_out_p);

  return 0;
}
