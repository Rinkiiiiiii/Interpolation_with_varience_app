#define MyAppName "Interpolation App"
#define MyAppVersion "1.2"
#define MyAppPublisher "Los Pitufos"
#define MyAppExeName "InterpolationApp.exe"

[Setup]
AppId={{CFEEF76F-D3EB-4671-A525-99E346C2E087}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Default location shown first, but user can change it
DefaultDirName={autopf}\Interpolation App
DefaultGroupName={#MyAppName}

UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes
DisableDirPage=no

OutputDir=C:\Users\pc\Work Stuff\Interpolation_with_varience_app\InterpolationAppInstaller
OutputBaseFilename=InterpolationAppSetup

Compression=lzma
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
CloseApplicationsFilter=*.exe
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\pc\Work Stuff\Interpolation_with_varience_app\dist\InterpolationApp.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent