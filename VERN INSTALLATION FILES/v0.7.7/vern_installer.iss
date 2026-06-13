; VERN Windows Installer — Inno Setup Script
; Version: 0.7.7
;
; Prerequisites:
;   - vern.exe (PyInstaller build) must be in the same directory as this script
;   - Inno Setup 6.x must be installed: https://jrsoftware.org/isinfo.php
;
; To compile: open in Inno Setup Compiler and press F9.
; Output: Output\vern_setup_v0.7.7.exe

[Setup]
AppId={{8F3A2B1C-4D5E-4F60-9A7B-C1D2E3F40077}
AppName=VERN
AppVersion=0.7.7
AppPublisher=The VERN Project
; {autopf} resolves to C:\Program Files on 64-bit Windows 10/11
DefaultDirName={autopf}\VERN
DefaultGroupName=The VERN Project\VERN
DisableProgramGroupPage=yes
OutputBaseFilename=vern_setup_v0.7.7
OutputDir=Output
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Administrator rights required to write to Program Files and HKLM PATH
PrivilegesRequired=admin
; Windows 10 minimum (build 10.0)
MinVersion=10.0
UninstallDisplayName=VERN 0.7.7
UninstallDisplayIcon={app}\vern.exe
VersionInfoVersion=0.7.7.0
VersionInfoDescription=VERN Interpreter Installer
VersionInfoCompany=The VERN Project
; Tells Inno Setup to broadcast WM_SETTINGCHANGE so open terminals pick up the
; new PATH without requiring a reboot
ChangesEnvironment=yes

[Files]
Source: "vern.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu entry under The VERN Project\VERN
Name: "{group}\VERN";           Filename: "{app}\vern.exe"
Name: "{group}\Uninstall VERN"; Filename: "{uninstallexe}"

[UninstallDelete]
; Remove the installation directory entirely on uninstall, even if empty
Type: filesandordirs; Name: "{app}"

[Code]

const
  EnvironmentKey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';

{ Read the current system PATH from the registry. }
function GetSystemPath: string;
var
  PathValue: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', PathValue) then
    PathValue := '';
  Result := PathValue;
end;

{ Write a new value back to the system PATH (REG_EXPAND_SZ).
  Uses RegWriteExpandStringValue which is the correct Inno Setup 6 function. }
procedure SetSystemPath(const NewPath: string);
begin
  RegWriteExpandStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', NewPath);
end;

{ Append Dir to the system PATH if it is not already present.
  Uses exact, case-insensitive, semicolon-delimited segment comparison to
  avoid false-positive matches against paths that share a common prefix. }
procedure AddToPath(const Dir: string);
var
  CurrentPath: string;
  Parts: TStringList;
  I: Integer;
  Found: Boolean;
begin
  CurrentPath := GetSystemPath;
  Parts := TStringList.Create;
  try
    Parts.Delimiter := ';';
    Parts.StrictDelimiter := True;
    Parts.DelimitedText := CurrentPath;
    Found := False;
    for I := 0 to Parts.Count - 1 do
      if LowerCase(Parts[I]) = LowerCase(Dir) then
      begin
        Found := True;
        Break;
      end;
    if not Found then
    begin
      if (Length(CurrentPath) > 0) and
         (CurrentPath[Length(CurrentPath)] <> ';') then
        SetSystemPath(CurrentPath + ';' + Dir)
      else
        SetSystemPath(CurrentPath + Dir);
    end;
  finally
    Parts.Free;
  end;
end;

{ Remove Dir from the system PATH, rebuilding the string from its
  semicolon-delimited segments and omitting any exact match for Dir. }
procedure RemoveFromPath(const Dir: string);
var
  CurrentPath, NewPath, Segment: string;
  Parts: TStringList;
  I: Integer;
begin
  CurrentPath := GetSystemPath;
  Parts := TStringList.Create;
  try
    Parts.Delimiter := ';';
    Parts.StrictDelimiter := True;
    Parts.DelimitedText := CurrentPath;
    NewPath := '';
    for I := 0 to Parts.Count - 1 do
    begin
      Segment := Parts[I];
      if (Segment <> '') and (LowerCase(Segment) <> LowerCase(Dir)) then
      begin
        if NewPath <> '' then
          NewPath := NewPath + ';';
        NewPath := NewPath + Segment;
      end;
    end;
    SetSystemPath(NewPath);
  finally
    Parts.Free;
  end;
end;

{ Add the install directory to the system PATH after all files are in place. }
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    AddToPath(ExpandConstant('{app}'));
end;

{ Remove the install directory from the system PATH during uninstall. }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RemoveFromPath(ExpandConstant('{app}'));
end;
