# SRX Dynamic Feed Update Test

Use this procedure to prove that feed updates propagate without a configuration commit.

## Update the feed archive

```bash
cd /var/www/html
echo 1.1.1.2 >> feed-1/whitelist-1
tar czf feed-1.tgz feed-1/
```

Watch the feed server:

```bash
tail -f -n0 /var/log/nginx/access.log
```

## Verify on SRX

```text
show log messages | match ipfd
show security dynamic-address
```

The new IP should appear under the mapped dynamic address object after the next update interval.
