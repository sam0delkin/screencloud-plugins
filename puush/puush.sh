curl --noproxy "*" "https://puush.me/api/up" -# -F "k=$1" -F "z=waifu" -F "f=@$2" | sed -E 's/^.+,(.+),.+,.+$/\1\n/'