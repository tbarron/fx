use std::collections::HashMap;
use super::*;

// ----------------------------------------------------------------------------
// Given an integer value in range or a valid error name, print
// information about that error. If a number is out of range or a name
// is not recognized, the failing keys are reported.
//
pub fn perrno(values: &[&str]) {
    let by_num = err_list();
    let by_name = index_by_name(&by_num);
    let bad_value = (-1, String::from(""), String::from(""));
    for item in values {
        let num = str_to_int32(item, -1);
        if 0 < num {
            let tup = match by_num.get(&num) {
                Some(tup) => &tup,
                None      => &bad_value
            };
            if 0 < tup.0 {
                println!("{} ({}): {}", tup.1, tup.0, tup.2);
            } else {
                println!("No error entry found for {}", num);
            }
            continue;
        }

        let s_item = String::from(*item);
        let tup = match by_name.get(&s_item) {
            Some(tup) => &tup,
            None      => &bad_value
        };
        if 0 < tup.0 {
            println!("{} ({}): {}", tup.1, tup.0, tup.2);
        } else {
            println!("No error entry found for {}", item);
        }
    }
}

// ----------------------------------------------------------------------------
// Given a hash map indexed by error number (i32), create a copy
// indexed by name (String).
//
fn index_by_name(by_num: &HashMap<i32, (i32, String, String)>)
                 -> HashMap<String, (i32, String, String)> {
    let mut var = HashMap::new();
    for item in by_num {
        let tup = item.1.clone();
        let key = tup.1.clone();
        var.insert(key, tup);
    }
    var
}

// ----------------------------------------------------------------------------
// This routine is the single source of truth for the known error
// numbers, error names, and error descriptions. It generates and
// returns a hash map indexed by error number (i32).
//
fn err_list() -> HashMap<i32, (i32, String, String)> {
    let mut var = HashMap::new();
    let errlist = [(1, "EPERM", "Operation not permitted"),
                   (2, "ENOENT", "No such file or directory"),
                   (3, "ESRCH", "No such process"),
                   (4, "EINTR", "Interrupted system call"),
                   (5, "EIO", "Input/output error"),
                   (6, "ENXIO", "Device not configured"),
                   (7, "E2BIG", "Argument list too long"),
                   (8, "ENOEXEC", "Exec format error"),
                   (9, "EBADF", "Bad file descriptor"),
                   (10, "ECHILD", "No child processes"),
                   (11, "EDEADLK", "Resource deadlock avoided"),
                   (12, "ENOMEM", "Cannot allocate memory"),
                   (13, "EACCES", "Permission denied"),
                   (14, "EFAULT", "Bad address"),
                   (15, "ENOTBLK", "Block device required"),
                   (16, "EBUSY", "Resource busy"),
                   (17, "EEXIST", "File exists"),
                   (18, "EXDEV", "Cross-device link"),
                   (19, "ENODEV", "Operation not supported by device"),
                   (20, "ENOTDIR", "Not a directory"),
                   (21, "EISDIR", "Is a directory"),
                   (22, "EINVAL", "Invalid argument"),
                   (23, "ENFILE", "Too many open files in system"),
                   (24, "EMFILE", "Too many open files"),
                   (25, "ENOTTY", "Inappropriate ioctl for device"),
                   (26, "ETXTBSY", "Text file busy"),
                   (27, "EFBIG", "File too large"),
                   (28, "ENOSPC", "No space left on device"),
                   (29, "ESPIPE", "Illegal seek"),
                   (30, "EROFS", "Read-only file system"),
                   (31, "EMLINK", "Too many links"),
                   (32, "EPIPE", "Broken pipe"),
                   (33, "EDOM", "Numerical argument out of domain"),
                   (34, "ERANGE", "Result too large"),
                   (35, "EWOULDBLOCK", "Resource temporarily unavailable"),
                   (36, "EINPROGRESS", "Operation now in progress"),
                   (37, "EALREADY", "Operation already in progress"),
                   (38, "ENOTSOCK", "Socket operation on non-socket"),
                   (39, "EDESTADDRREQ", "Destination address required"),
                   (40, "EMSGSIZE", "Message too long"),
                   (41, "EPROTOTYPE", "Protocol wrong type for socket"),
                   (42, "ENOPROTOOPT", "Protocol not available"),
                   (43, "EPROTONOSUPPORT", "Protocol not supported"),
                   (44, "ESOCKTNOSUPPORT", "Socket type not supported"),
                   (45, "ENOTSUP", "Operation not supported"),
                   (46, "EPFNOSUPPORT", "Protocol family not supported"),
                   (47, "EAFNOSUPPORT", "Address family not supported by protocol family"),
                   (48, "EADDRINUSE", "Address already in use"),
                   (49, "EADDRNOTAVAIL", "Can't assign requested address"),
                   (50, "ENETDOWN", "Network is down"),
                   (51, "ENETUNREACH", "Network is unreachable"),
                   (52, "ENETRESET", "Network dropped connection on reset"),
                   (53, "ECONNABORTED", "Software caused connection abort"),
                   (54, "ECONNRESET", "Connection reset by peer"),
                   (55, "ENOBUFS", "No buffer space available"),
                   (56, "EISCONN", "Socket is already connected"),
                   (57, "ENOTCONN", "Socket is not connected"),
                   (58, "ESHUTDOWN", "Can't send after socket shutdown"),
                   (59, "ETOOMANYREFS", "Too many references: can't splice"),
                   (60, "ETIMEDOUT", "Operation timed out"),
                   (61, "ECONNREFUSED", "Connection refused"),
                   (62, "ELOOP", "Too many levels of symbolic links"),
                   (63, "ENAMETOOLONG", "File name too long"),
                   (64, "EHOSTDOWN", "Host is down"),
                   (65, "EHOSTUNREACH", "No route to host"),
                   (66, "ENOTEMPTY", "Directory not empty"),
                   (67, "EPROCLIM", "Too many processes"),
                   (68, "EUSERS", "Too many users"),
                   (69, "EDQUOT", "Disc quota exceeded"),
                   (70, "ESTALE", "Stale NFS file handle"),
                   (71, "EREMOTE", "Too many levels of remote in path"),
                   (72, "EBADRPC", "RPC struct is bad"),
                   (73, "ERPCMISMATCH", "RPC version wrong"),
                   (74, "EPROGUNAVAIL", "RPC prog. not avail"),
                   (75, "EPROGMISMATCH", "Program version wrong"),
                   (76, "EPROCUNAVAIL", "Bad procedure for program"),
                   (77, "ENOLCK", "No locks available"),
                   (78, "ENOSYS", "Function not implemented"),
                   (79, "EFTYPE", "Inappropriate file type or format"),
                   (80, "EAUTH", "Authentication error"),
                   (81, "ENEEDAUTH", "Need authenticator"),
                   (82, "EPWROFF", "Device power is off"),
                   (83, "EDEVERR", "Device error"),
                   (84, "EOVERFLOW", "Value too large to be stored in data type"),
                   (85, "EBADEXEC", "Bad executable (or shared library)"),
                   (86, "EBADARCH", "Bad CPU type in executable"),
                   (87, "ESHLIBVERS", "Shared library version mismatch"),
                   (88, "EBADMACHO", "Malformed Mach-o file"),
                   (89, "ECANCELED", "Operation canceled"),
                   (90, "EIDRM", "Identifier removed"),
                   (91, "ENOMSG", "No message of desired type"),
                   (92, "EILSEQ", "Illegal byte sequence"),
                   (93, "ENOATTR", "Attribute not found"),
                   (94, "EBADMSG", "Bad message"),
                   (95, "EMULTIHOP", "EMULTIHOP (Reserved)"),
                   (96, "ENODATA", "No message available on STREAM"),
                   (97, "ENOLINK", "ENOLINK (Reserved)"),
                   (98, "ENOSR", "No STREAM resources"),
                   (99, "ENOSTR", "Not a STREAM"),
                   (100, "EPROTO", "Protocol error"),
                   (101, "ETIME", "STREAM ioctl timeout"),
                   (102, "EOPNOTSUPP", "Operation not supported on socket"),
                   (103, "ENOPOLICY", "Policy not found"),
                   (104, "ENOTRECOVERABLE", "State not recoverable"),
                   (105, "EOWNERDEAD", "Previous owner died"),
    ];
    for item in errlist.iter() {
        var.insert(item.0, (item.0, String::from(item.1), String::from(item.2)));
    }
    var
}
