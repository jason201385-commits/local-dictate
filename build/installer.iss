; Inno Setup 安裝腳本 — local-dictate
;
; 編譯：把 PyInstaller 的產物放到 dist\local-dictate\ 之後
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss
;
; 刻意的決定：
;   · PrivilegesRequired=lowest — per-user 安裝，不跳 UAC。
;     一般使用者看到「需要管理員權限」會直接放棄，而且公司電腦常常沒有。
;   · AppId 固定 — 升級時覆蓋舊版，不會裝出第二份。改了這個 GUID 就會裝兩套。
;   · 使用者資料不放安裝目錄 — 程式寫在 %LOCALAPPDATA%\local-dictate\，
;     解除安裝時另外詢問要不要刪。模型可能好幾 GB，不該默默清掉。
;   · 開機啟動預設不勾 — 偷偷常駐會直接扣信任分。

#define AppName "local-dictate"
#define AppVersion "0.1.0"
#define AppPublisher "local-dictate contributors"
#define AppURL "https://github.com/jason201385-commits/local-dictate"
#define AppExeName "local-dictate.exe"

[Setup]
AppId={{9F3C1A6E-4D7B-4E21-9C5A-0E7B2D6F8A31}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=local-dictate-setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExeName}
; 免安裝需求說明：不需要 Python
AppComments=Local Traditional-Chinese voice dictation. Audio never leaves your machine.

; ⚠️ 繁體中文是 Inno Setup 的「非官方翻譯」，**預設安裝裡沒有這個檔**
;    （2026-07-26 CI 實際踩到：Couldn't open include file ChineseTraditional.isl）。
;    所以這裡用 FileExists 判斷：有就加繁中，沒有就只出英文。
;    絕對不要讓一個翻譯檔有能力擋掉整個 release。
#define ChtIsl AddBackslash(CompilerPath) + "Languages\ChineseTraditional.isl"
#define HasCht FileExists(ChtIsl)

[Languages]
; 英文一定要在，而且要放第一個 —— Inno 至少需要一種語言
Name: "en"; MessagesFile: "compiler:Default.isl"
#if HasCht
Name: "cht"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"
#endif

[CustomMessages]
en.AutoStart=Start automatically when Windows starts
en.CreateDesktopIcon=Create a desktop shortcut
en.LaunchAfter=Launch now
en.KeepData=Keep your settings, vocabulary and downloaded models?%n%nModels can take several GB. Choosing No deletes them.
#if HasCht
cht.AutoStart=開機時自動啟動（背景執行，不佔畫面）
cht.CreateDesktopIcon=建立桌面捷徑
cht.LaunchAfter=現在就開始使用
cht.KeepData=保留你的設定、專有名詞字典與語音模型？%n%n模型可能佔用數 GB。選「否」會一併刪除。
#endif

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
; 開機啟動預設不勾 —— 讓使用者自己決定
Name: "autostart"; Description: "{cm:AutoStart}"; Flags: unchecked

[Files]
Source: "..\dist\local-dictate\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 內建 base 模型（141MB），讓第一次啟動不用等下載。
; 建置時把模型放到 build\bundled-model\ 底下，沒有的話這行會被跳過。
Source: "bundled-model\*"; DestDir: "{localappdata}\local-dictate\models"; \
    Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: autostart

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchAfter}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 只清程式自己產生的暫存，使用者資料另外問（見 InitializeUninstall）
Type: filesandordirs; Name: "{app}\_internal\__pycache__"

[Code]
// 解除安裝時詢問是否保留使用者資料。
// 不要默默刪掉——模型可能幾 GB，重下載很痛；字典是使用者自己累積的。
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\local-dictate');
    if DirExists(DataDir) then
    begin
      if MsgBox(ExpandConstant('{cm:KeepData}'), mbConfirmation, MB_YESNO) = IDNO then
        DelTree(DataDir, True, True, True);
    end;
  end;
end;
