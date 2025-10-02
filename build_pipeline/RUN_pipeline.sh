# Run the pipeline to get the sequences, format them and build the databases

DIR="."

# Rip the sequences from the imgt website. HTML may change in the future. 
which python
mkdir -p $DIR/IMGT_sequence_files/htmlfiles
mkdir -p $DIR/IMGT_sequence_files/fastafiles
python $DIR/RipIMGT.py

echo "FINISHED RIPIMGT"

# Format the alignments and handle imgt oddities to put into a consistent alignment format
mkdir -p $DIR/curated_alignments
mkdir -p $DIR/muscle_alignments
which python
python $DIR/FormatAlignments.py

echo "FINISHED FORMATALIGNMENTS"

# Build the hmms for each species and chain.
# --hand option required otherwise it will delete columns that are mainly gaps. We want 128 columns otherwise ARNACI will fall over.
mkdir -p $DIR/HMMs
which hmmbuild
echo "Starting HMMBUILD"
hmmbuild --hand $DIR/HMMs/ALL.hmm $DIR/curated_alignments/ALL.stockholm
echo "FINISHED HMMBUILD"
#hmmbuild --hand $DIR/HMMs/ALL_AND_C.hmm $DIR/curated_alignments/ALL_AND_C.stockholm

# Turn the output HMMs file into a binary form. This is required for hmmscan that is used in ARNACI.
which hmmpress
echo "Starting HMMPRESS"
hmmpress -f $DIR/HMMs/ALL.hmm 
echo "FINISHED HMMPRESS"
#hmmpress -f $DIR/HMMs/ALL_AND_C.hmm

