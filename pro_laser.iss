[Setup]
; 應用程式的基本資訊
AppId={{9A3B5C7D-1E2F-4A5B-8C9D-0E1F2A3B4C5D}
AppName=虛擬雷射筆 (Virtual Laser Pointer)
AppVersion=1.0.0
AppPublisher=團隊 OneWAY
; 預設安裝路徑 (Program Files)
DefaultDirName={autopf}\VirtualLaserPointer
; 開始功能表資料夾名稱
DefaultGroupName=虛擬雷射筆
; 安裝檔輸出的資料夾 (設定輸出到 dist 資料夾內)
OutputDir=dist
; 生成的安裝檔名稱
OutputBaseFilename=VirtualLaserPointer_Setup_v1.0
; 安裝程式本身的圖示 (讀取同資料夾的 red_dot.ico)
SetupIconFile=red_dot.ico
; ✅ 修正重點：指定 Windows「應用程式與功能」列表顯示的圖示
UninstallDisplayIcon={app}\pro_laser.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; 移除安裝結束後詢問是否重啟電腦的選項
RestartIfNeededByRun=no

[Languages]
; 設定安裝介面為預設語言 (英文)
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; 讓使用者勾選是否建立桌面捷徑 (預設打勾)
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; 精準指定從 dist 資料夾中讀取 pro_laser.exe
Source: "dist\pro_laser.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 建立開始功能表捷徑
Name: "{group}\虛擬雷射筆"; Filename: "{app}\pro_laser.exe"; IconFilename: "{app}\pro_laser.exe"
; 建立解除安裝的捷徑
Name: "{group}\解除安裝 虛擬雷射筆"; Filename: "{uninstallexe}"
; 建立桌面捷徑
Name: "{autodesktop}\虛擬雷射筆"; Filename: "{app}\pro_laser.exe"; Tasks: desktopicon; IconFilename: "{app}\pro_laser.exe"

[Run]
; 安裝完成後，提供「立即執行」的打勾選項
Filename: "{app}\pro_laser.exe"; Description: "啟動 虛擬雷射筆"; Flags: nowait postinstall skipifsilent