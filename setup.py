import shutil, os, subprocess
import site, sys
from importlib import util
from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        # Post-installation routine
        ANARCI_LOC = os.path.join(site.getsitepackages()[0], 'anarci') # site-packages/ folder
        ANARCI_BIN = sys.executable.split('python')[0] # bin/ folder

        shutil.copy('bin/ANARCI', ANARCI_BIN) # copy ANARCI executable
        print("INFO: ANARCI lives in: ", ANARCI_LOC) 

        # Build HMMs from IMGT germlines
        print('INFO: Downloading germlines from IMGT and building HMMs...')
        print("INFO: running 'RUN_pipeline.sh', this will take a couple a minutes.")
        env = os.environ.copy()
        env["PYTHON_SCRIPT"] = sys.executable
        print("INFO: Running 'RUN_pipeline.sh' with Python script: ", env["PYTHON_SCRIPT"])

        with open("build_pipeline.log", "w") as logfile:
            proc = subprocess.Popen(
                ["bash", "RUN_pipeline.sh"],
                stdout=logfile,
                stderr=subprocess.STDOUT,
                env=env,
                cwd="build_pipeline",
            )
            proc.wait()
        
        # # Copy HMMs where ANARCI can find them
        print("INFO: Copying generated files to ANARCI installation directory...")
        shutil.copy("build_pipeline/curated_alignments/germlines.py", ANARCI_LOC)
        
        # Create dat directory if it doesn't exist
        dat_dir = os.path.join(ANARCI_LOC, "dat")
        if not os.path.exists(dat_dir):
            os.makedirs(dat_dir)
        
        # Copy HMMs directory
        hmm_dest = os.path.join(ANARCI_LOC, "dat", "HMMs")
        if os.path.exists(hmm_dest):
            shutil.rmtree(hmm_dest)
        shutil.copytree("HMMs", hmm_dest)
        print("INFO: HMM files copied to:", hmm_dest)
        
        # Remove temporary data from HMMs generation (optional cleanup)
        try:
            shutil.rmtree("curated_alignments/")
            shutil.rmtree("muscle_alignments/")
            shutil.rmtree("HMMs/")
            shutil.rmtree("IMGT_sequence_files/")
            print("INFO: Cleaned up temporary build files")
        except OSError as e:
            print("WARNING: Could not clean up some temporary files:", e)

setup(
    name='anarci',
    version='1.3',
    description='Antibody Numbering and Receptor ClassIfication',
    author='James Dunbar',
    author_email='opig@stats.ox.ac.uk',
    url='http://opig.stats.ox.ac.uk/webapps/ANARCI',
    packages=['anarci'],
    package_dir={'anarci': 'lib/python/anarci'},
    data_files=[('bin', ['bin/muscle', 'bin/muscle_macOS', 'bin/ANARCI'])],
    include_package_data=True,
    scripts=['bin/ANARCI'],
    cmdclass={"install": CustomInstallCommand},
    zip_safe=False,  # Important: prevents wheel building issues
)
