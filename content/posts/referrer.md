---
title: "Disable your referrer header by default"
date: 2023-01-08T11:48:10+01:00
draft: false
---

In HTTP, there exists a header caller `Referer`, which contains information about which site you are coming from when following a link [^1].
It can contain a partial, or complete URL.
Obviously, this has privacy implications.
This is why in much self-hosted software for instance, you will see the `Referrer-Policy` header being set to `no-referrer` [^2].

In Firefox, the default behaviour is to transmit referrer information.
If you don't want this behaviour, there exists the option `network.http.referer.defaultPolicy` in `about:config`.
For a couple of weeks I have set it to `0`, and it has given me almost no problems.
Turns out, if a website cares about your referrer, they will explicitly state what they expect in a header or in the `<head>` [^3].
Therefore, I whole-heartedly recommend setting this header.

For more information, see the [Firefox documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy).

[^1]: "Referer" is a historic mispelling, which stays in the standard.
[^2]: For instance, see [Miniflux](https://github.com/miniflux/v2/blob/992422c91f2fc90949d8cd9511622bffaa270ae6/http/response/builder.go#L95), my preferred RSS reader
[^3]: Except when I tried to sign up for brilliant.org. Shame on you.
