script_dir=$(cd ${BASH_SOURCE%/*}; pwd)

set -e 

spielart=${1:-EJ} 
case $spielart in
  LOTTO|EJ|GS|KENO|EW|AW)
    true
    ;;
  *)
    false
    ;;
esac
jahr_bis=${2:-2020}
jahr_von=${3:-2019}

mkdir -p file
curl -S "https://ergebnisse.westlotto.com/wlinfo/WL_InfoService?gruppe=ErgebnisDownload&client=sachsen&jahr_von=$jahr_von&jahr_bis=$jahr_bis&spielart=$spielart&format=csv" --output file/file.zip
( cd file; unzip file.zip; rm file.zip; )
mv file/* "$script_dir/data/sachsenlotto.de/eurojackpot/"
