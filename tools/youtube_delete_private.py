"""旧版（非公開試写用）YouTube 動画の削除。

修正版（新版）のアップロード後、新版の処理完了を確認してから、旧版が非公開であることを
確認したうえで削除する（削除は取り消し不可）。方針はユーザーメモリ
`youtube-delete-superseded-uploads`（修正アップロード後 → 新IDの処理完了確認 → 旧ID削除）。

使い方（script-to-video の venv から実行する。PYTHONUTF8=1 推奨）:

  C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe \\
      tools\\youtube_delete_private.py --new-id <新ID> --old-id <旧ID> [--yes]

手順:
  1. 新版 (--new-id) の uploadStatus が processed かつ privacyStatus が private になるまで
     待つ（最大 --wait-seconds 秒、--poll-interval 秒おきに確認。既定 600秒/60秒）。
  2. 旧版 (--old-id) の privacyStatus を確認する。private でなければ削除せず終了する
     （public / unlisted の場合は事故防止のため必ず中断する）。
  3. --yes が付いていれば旧版を削除する（付いていなければ内容を表示して終了、削除しない）。
  4. 削除後、旧版の videos().list が空になることを確認する。

認証は script-to-video の youtube_upload.load_credentials を再利用する（トークンの
リフレッシュのみ、ブラウザは開かない）。既定トークンは「ずんだ人文学」チャンネル用
(secrets/youtube_token_kamishibai.json)。他チャンネルで使う場合は --token を指定する。
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

STV_ROOT = Path(r"C:\Users\shuya\Projects\script-to-video")
sys.path.insert(0, str(STV_ROOT / "src"))

from script_to_video.youtube_upload import load_credentials  # noqa: E402

DEFAULT_CLIENT_SECRET = STV_ROOT / "secrets" / "client_secret.json"
DEFAULT_TOKEN = STV_ROOT / "secrets" / "youtube_token_kamishibai.json"


def service(client_secret: Path, token: Path):
    from googleapiclient.discovery import build

    creds = load_credentials(client_secret, token)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def get_status(yt, video_id: str):
    resp = yt.videos().list(part="snippet,status,processingDetails", id=video_id).execute()
    items = resp.get("items") or []
    if not items:
        return None
    return items[0]


def wait_for_processed(yt, video_id: str, wait_seconds: int, poll_interval: int):
    deadline = time.monotonic() + wait_seconds
    while True:
        v = get_status(yt, video_id)
        if v is None:
            raise SystemExit(f"新版が見つかりません: {video_id}")
        st = v["status"]
        pd = v.get("processingDetails", {})
        upload_status = st.get("uploadStatus")
        privacy = st.get("privacyStatus")
        processing_status = pd.get("processingStatus")
        print(
            f"[新版 {video_id}] uploadStatus={upload_status} privacyStatus={privacy} "
            f"processingStatus={processing_status}"
        )
        if upload_status == "processed" and privacy == "private":
            return v
        if time.monotonic() >= deadline:
            raise SystemExit(
                f"新版の処理が {wait_seconds} 秒以内に完了しませんでした（最終状態: "
                f"uploadStatus={upload_status} privacyStatus={privacy} "
                f"processingStatus={processing_status}）"
            )
        time.sleep(poll_interval)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--new-id", required=True, help="残す新版の動画ID")
    ap.add_argument("--old-id", required=True, help="削除する旧版の動画ID")
    ap.add_argument("--client-secret", type=Path, default=DEFAULT_CLIENT_SECRET)
    ap.add_argument("--token", type=Path, default=DEFAULT_TOKEN)
    ap.add_argument("--wait-seconds", type=int, default=600, help="新版の処理完了を待つ最大秒数")
    ap.add_argument("--poll-interval", type=int, default=60, help="新版の状態を確認する間隔（秒）")
    ap.add_argument("--yes", action="store_true", help="削除を実際に実行する（付けないと確認のみ）")
    a = ap.parse_args()

    yt = service(a.client_secret, a.token)

    print("=== 1. 新版の処理状況を確認 ===")
    wait_for_processed(yt, a.new_id, a.wait_seconds, a.poll_interval)
    print("新版は処理完了・非公開です。")

    print("=== 2. 旧版の状態を確認 ===")
    old = get_status(yt, a.old_id)
    if old is None:
        print(f"旧版が見つかりません（既に削除済みの可能性）: {a.old_id}")
        return 0
    title = old["snippet"].get("title")
    privacy = old["status"].get("privacyStatus")
    print(f"[旧版 {a.old_id}] title={title} privacyStatus={privacy}")
    if privacy != "private":
        print(f"旧版が非公開ではありません（privacyStatus={privacy}）。削除せず終了します。")
        return 1

    print("=== 3. 旧版を削除 ===")
    if not a.yes:
        print("--yes が無いので削除は実行しません。")
        return 2
    yt.videos().delete(id=a.old_id).execute()
    print(f"削除しました: {a.old_id}")

    print("=== 4. 削除の確認 ===")
    confirm = get_status(yt, a.old_id)
    if confirm is None:
        print("旧版は取得できなくなりました（削除確認OK）。")
        return 0
    print("警告: 削除後も旧版が取得できます。手動確認してください。")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
