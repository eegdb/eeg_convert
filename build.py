import PyInstaller.__main__

PyInstaller.__main__.run([
    'eeg_convert/main.py',                # 入口脚本
    '--onefile',              # 打包成单个 exe
    '--name=EEGConvert',           # 可选：指定 exe 名称
    '--collect-all', 'mne',
    '--exclude-module', 'mne.viz',
    '--exclude-module', 'mne.gui',
    '--exclude-module', 'mne.datasets',
    '--exclude-module', 'mne.report',
    '--exclude-module', 'mne.preprocessing',
    '--exclude-module', 'mne.decoding',
])