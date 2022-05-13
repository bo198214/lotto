script_dir=$(cd "$(dirname "$BASH_SOURCE")"; pwd)

set -e 

spielart=${1:-EJ} 
case $spielart in
  LOTTO)
    jahr_von_default=1955
    ;;
  EJ)
    jahr_von_default=2012
    ;;
  GS)
    ;;
  KENO)
    ;;
  EW)
    ;;
  AW)
    ;;
  *)
    false
    ;;
esac
gruppe=ErgebnisDownload
case $gruppe in
  ErgebnisDownload|ZahlenUndQuoten)
    true
    ;;
  *)
    false
    ;;
esac

jahr_bis_default=$(date +%Y)

jahr_bis=${2:-$jahr_bis_default}
jahr_von=${3:-$jahr_von_default}

mkdir -p file
curl -S "https://ergebnisse.westlotto.com/wlinfo/WL_InfoService?gruppe=ErgebnisDownload&client=sachsen&jahr_von=$jahr_von&jahr_bis=$jahr_bis&spielart=$spielart&format=csv" --output file/file.zip
( cd file; unzip file.zip; rm file.zip; )
if [ $jahr_von_default = $jahr_von ] && [ $jahr_bis_default = $jahr_bis ]
then
  d="$script_dir/data/westlotto/$spielart/"
  mkdir -p "$d"
  mv file/* "$d"
fi
