#!/bin/zsh
set -eu

project_dir=${0:A:h:h}
workspace_dir=${project_dir:h}
asset_root="$project_dir/assets/roots"
mkdir -p "$asset_root"

render_pair() {
  local id=$1
  local qp_path=$2
  local qp_first=$3
  local qp_last=$4
  local ms_path=$5
  local ms_first=$6
  local ms_last=$7
  local target="$asset_root/$id"
  mkdir -p "$target"
  pdftoppm -png -r 110 -f "$qp_first" -l "$qp_last" "$workspace_dir/$qp_path" "$target/qp" >/dev/null 2>&1
  pdftoppm -png -r 110 -f "$ms_first" -l "$ms_last" "$workspace_dir/$ms_path" "$target/ms" >/dev/null 2>&1
}

render_pair 2019-mj-11-12 '2019/2019/9231_s19_qp_11.pdf' 10 11 '2019/2019/9231_s19_ms_11.pdf' 10 11
render_pair 2019-mj-13 '2019/2019/9231_s19_qp_13.pdf' 16 17 '2019/2019/9231_s19_ms_13.pdf' 14 15
render_pair 2019-on-11-13 '2019/2019/9231_w19_qp_11.pdf' 10 11 '2019/2019/9231_w19_ms_11.pdf' 12 13

render_pair 2020-mj-11-12 '2020/2020/9231_s20_qp_11.pdf' 4 5 '2020/2020/9231_s20_ms_11.pdf' 8 9
render_pair 2020-mj-13 '2020/2020/9231_s20_qp_13.pdf' 2 3 '2020/2020/9231_s20_ms_13.pdf' 6 7
render_pair 2020-on-11-13 '2020/2020/9231_w20_qp_11.pdf' 6 7 '2020/2020/9231_w20_ms_11.pdf' 8 9
render_pair 2020-on-12 '2020/2020/9231_w20_qp_12.pdf' 3 4 '2020/2020/9231_w20_ms_12.pdf' 6 7

render_pair 2021-mj-11-12 '2021/2021/9231_s21_qp_11.pdf' 6 7 '2021/2021/9231_s21_ms_11.pdf' 7 8
render_pair 2021-mj-13 '2021/2021/9231_s21_qp_13.pdf' 4 5 '2021/2021/9231_s21_ms_13.pdf' 7 8
render_pair 2021-on-11-13 '2021/2021/9231_w21_qp_11.pdf' 2 3 '2021/2021/9231_w21_ms_11.pdf' 3 4
render_pair 2021-on-12 '2021/2021/9231_w21_qp_12.pdf' 6 7 '2021/2021/9231_w21_ms_12.pdf' 8 9

render_pair 2022-mj-11-12 '2022/2022/9231_s22_qp_11.pdf' 8 9 '2022/2022/9231_s22_ms_11.pdf' 9 10
render_pair 2022-mj-13 '2022/2022/9231_s22_qp_13.pdf' 4 5 '2022/2022/9231_s22_ms_13.pdf' 8 9

render_pair 2023-on-11-13 '2023/2023/9231_w23_qp_11.pdf' 5 5 '2023/2023/9231_w23_ms_11.pdf' 8 9
render_pair 2023-on-12 '2023/2023/9231_w23_qp_12.pdf' 6 7 '2023/2023/9231_w23_ms_12.pdf' 9 10

render_pair 2024-mj-11-12 '2024/2024/qp-202406-further mathematics-p11.pdf.pdf' 2 3 '2024/2024/ms-202406-further mathematics-p11.pdf.pdf' 6 7
render_pair 2024-mj-13 '2024/2024/qp-202406-further mathematics-p13.pdf.pdf' 4 5 '2024/2024/ms-202406-further mathematics-p13.pdf.pdf' 7 8
render_pair 2024-on-11-13 '2024/2024/qp-202410-further mathematics-p11.pdf.pdf' 6 7 '2024/2024/ms-202410-further mathematics-p11.pdf.pdf' 8 9
render_pair 2024-on-12 '2024/2024/qp-202410-further mathematics-p12.pdf.pdf' 6 7 '2024/2024/ms-202410-further mathematics-p12.pdf.pdf' 7 8

render_pair 2025-mj-11-12 '2025/2025/qp-202505-further mathematics-p11.pdf.pdf' 4 5 '2025/2025/ms-202505-further mathematics-p11.pdf.pdf' 10 11
render_pair 2025-mj-13 '2025/2025/qp-202505-further mathematics-p13.pdf.pdf' 6 7 '2025/2025/ms-202505-further mathematics-p13.pdf.pdf' 11 12
render_pair 2025-mj-14 '2025/2025/qp-202505-further mathematics-p14.pdf.pdf' 8 9 '2025/2025/ms-202505-further mathematics-p14.pdf.pdf' 12 13
render_pair 2025-on-11-13 '2025/2025/qp-202510-furthermathematics-p11.pdf.pdf' 8 9 '2025/2025/ms-202510-furthermathematics-p11.pdf.pdf' 11 12
render_pair 2025-on-12 '2025/2025/qp-202510-furthermathematics-p12.pdf.pdf' 4 5 '2025/2025/ms-202510-furthermathematics-p12.pdf.pdf' 10 11
render_pair 2025-on-14 '2025/2025/qp-202510-furthermathematics-p14.pdf.pdf' 4 5 '2025/2025/ms-202510-furthermathematics-p14.pdf.pdf' 9 10

print "Rendered $(find "$asset_root" -type f -name '*.png' | wc -l | tr -d '[:space:]') images."
