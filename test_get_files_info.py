from functions.get_files_info import get_files_info

if __name__ == "__main__":
    print("Result for current directory:\n", get_files_info("calculator", "."))
    print("Result for 'pkg' directory:\n", get_files_info("calculator", "pkg"))
    print("Result for '/bin' directory:\n", get_files_info("calculator", "/bin"))
    print("Result for '../' directory:\n", get_files_info("calculator", "../"))
