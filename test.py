import random
from library.services import (
    create_author, delete_author, get_all_authors,
    create_book, search_books_by_title,
    create_student, update_student_grade,
    borrow_book, return_book,
    get_student_borrow_count,
    get_currently_borrowed_books,
    get_overdue_borrows,
)

def main():
    print("=== Kutubxona Tizimi Final Exam Test Jarayoni ===\n")
    rand_id = random.randint(100, 999)

    # 1. Mualliflar testi
    print("--- 1. Author Test ---")
    a1 = create_author(f"Abdulla Qodiriy {rand_id}", "O'zbek romanchiligi asoschisi")
    a2 = create_author(f"O'tkir Hoshimov {rand_id}", "Mashhur yozuvchi")
    print(f"✅ Mualliflar yaratildi: {a1.name}, {a2.name}")

    # 2. Kitoblar testi
    print("\n--- 2. Book Test ---")
    b1 = create_book("O'tkan kunlar", a1.id, 1922, f"978{rand_id}01")
    b2 = create_book("Mehrobdan Chayon", a1.id, 1928, f"978{rand_id}02")
    b3 = create_book("Dunyoning ishlari", a2.id, 1982, f"978{rand_id}03")
    b4 = create_book("Ikki eshik orasi", a2.id, 1986, f"978{rand_id}04")
    print(f"✅ Kitoblar yaratildi: {b1.title}, {b3.title}")
    
    # Qidiruv testi
    search_res = search_books_by_title("kunlar")
    print(f"🔍 Qidiruv natijasi ('kunlar'): {len(search_res)} ta kitob topildi.")

    # 3. Talabalar testi
    print("\n--- 3. Student Test ---")
    s1 = create_student("Asadbek Toshkentov", f"asad{rand_id}@example.com", "3-kurs")
    print(f"✅ Talaba yaratildi: {s1.full_name}")
    
    # Grade update testi
    updated_s1 = update_student_grade(s1.id, "Bitiruvchi")
    print(f"🆙 Talaba kursi yangilandi: {updated_s1.grade}")

    # 4. Borrow Logic & Limit Test (3 tadan ortiq kitob berishni tekshirish)
    print("\n--- 4. Borrow Logic & Limit Test ---")
    borrow_book(s1.id, b1.id) # 1-kitob
    borrow_book(s1.id, b2.id) # 2-kitob
    borrow_book(s1.id, b3.id) # 3-kitob
    
    # 4-kitobni olishga urinish (Limit 3 ta bo'lishi kerak)
    b4_attempt = borrow_book(s1.id, b4.id)
    if b4_attempt is None:
        print("✅ Limit testi: Talabaga 4-kitob berilmadi (To'g'ri!)")
    else:
        print("❌ Xato: Talabaga 3 tadan ortiq kitob berib yuborildi!")

    # 5. Qaytarish testi
    print("\n--- 5. Return Test ---")
    # b1 ni qaytaramiz
    all_borrows = get_currently_borrowed_books()
    if all_borrows:
        # Hozirgi borrow yozuvlaridan birini olamiz
        res = return_book(1) # Soddalik uchun id=1 yoki bazadagi real id
        print(f"🔄 Kitob qaytarish bajarildi.")

    # 6. Delete Logic Test (Kitobi bor muallifni o'chirib ko'rish)
    print("\n--- 6. Delete Restriction Test ---")
    del_res = delete_author(a1.id)
    if not del_res:
        print(f"✅ O'chirish cheklovi testi: Kitobi bor muallif ({a1.name}) o'chirilmadi (To'g'ri!)")
    else:
        print("❌ Xato: Kitobi bor muallif o'chirib yuborildi!")

    # 7. Statistika
    print("\n--- 7. Statistics ---")
    overdue = get_overdue_borrows()
    print(f"⏳ Muddati o'tgan kitoblar soni: {len(overdue)}")
    
    borrow_count = get_student_borrow_count(s1.id)
    print(f"📊 {s1.full_name} jami olgan kitoblari: {borrow_count} ta")

    
if __name__ == "__main__":
    main()