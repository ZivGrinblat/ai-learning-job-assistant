#include <iostream>
#include <vector>
#include <fstream>
#include <string>

class Student {
private:
    std::string first_name = "First";
    std::string last_name = "Last";
    int m_id = 0;
    float m_average = 0;

public:
    Student() = default;

    Student(std::string first_name, std::string last_name, int id, float avg)
        : first_name(std::move(first_name)),
          last_name(std::move(last_name)),
          m_id(id),
          m_average(avg) {}

    float getAvg() const { return m_average; }

    int getId() const { return m_id; }

    std::string getFirstName() const { return first_name; }

    std::string getLastName() const { return last_name; }

    void print() const {
        std::cout << "First name: " << first_name << "\n"
                  << "Last name: " << last_name << "\n"
                  << "ID: " << m_id << "\n"
                  << "Average: " << m_average << "\n";
    }
};

class Course {
private:
    std::string course_name = "Course";
    std::vector<Student> course_students;

public:
    Course() = default;

    explicit Course(const std::string& name) : course_name(name) {}

    void addStudent(const Student& s) { course_students.push_back(s); }

    const std::vector<Student>& getStudents() const { return course_students; }

    void print() const {
        std::cout << "Course: " << course_name << "\n";
        for (const auto& s : course_students) {
            s.print();
        }
    }

    void loadFromFile(const std::string& filename) {
        std::ifstream fin(filename);
        if (!fin.is_open()) {
            std::cerr << "Could not open file: " << filename << "\n";
            return;
        }

        std::string first_name, last_name;
        int id;
        float avg;

        while (fin >> first_name >> last_name >> id >> avg) {
            addStudent(Student(first_name, last_name, id, avg));
        }
    }
};

int main() {
    std::string first_name = "Ziv";
    std::string last_name = "Grinblat";
    std::string full_name = first_name + " " + last_name;

    std::cout << first_name << " " << last_name << std::endl;
    std::cout << full_name << std::endl;
    std::cout << "Hello World!" << std::endl;

    std::vector<int> vec;
    vec.push_back(42);
    vec.push_back(10);
    vec.push_back(12);

    std::cout << "Vec[0] = " << vec[0] << std::endl;
    std::cout << "Vec[1] = " << vec[1] << std::endl;

    for (size_t i = 0; i < vec.size(); i++) {
        std::cout << vec[i] << std::endl;
    }

    return 0;
}
