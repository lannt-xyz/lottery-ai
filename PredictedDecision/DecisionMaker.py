import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

class DecisionMaker:
    def __init__(self, city_code):
        load_dotenv()

        self.data_dir = os.getenv('STORE_DIR')
        self.file_path = f'{self.data_dir}/{city_code}.csv'

        # TODO: this only for testing
        # self.file_path = f'../crawing-data/xosomiennam/{city_code}.csv'

    def most_common(self, lst):
        return max(set(lst), key=lst.count)

    def most_consistent_cycle(self, numbers_to_predict):
        # Đọc dữ liệu từ file CSV không có tiêu đề
        data = pd.read_csv(self.file_path, header=None)  # Thay 'path_to_your_file.csv' bằng đường dẫn đến file của bạn
        
        # Lưu trữ độ lệch chuẩn của chu kỳ cho từng số
        cycle_std_devs = {}

        # Duyệt qua từng số trong danh sách cần dự đoán
        for number_to_predict in numbers_to_predict:
            occurrences = []
            
            # Duyệt qua các dòng dữ liệu và ghi lại vị trí (index) mà số đó xuất hiện
            for idx, row in data.iterrows():
                if number_to_predict in row.values:
                    occurrences.append(idx)
            
            if len(occurrences) < 2:
                print(f"Số {number_to_predict} xuất hiện ít hơn 2 lần, không đủ dữ liệu để phân tích chu kỳ.")
                continue
            
            # Tính chu kỳ (khoảng cách) giữa các lần xuất hiện liên tiếp
            cycles = np.diff(occurrences)
            
            # Tính độ lệch chuẩn của chu kỳ
            std_dev = np.std(cycles)
            cycle_std_devs[number_to_predict] = std_dev

        # Tìm con số có chu kỳ đều nhất (độ lệch chuẩn thấp nhất)
        most_consistent_number = min(cycle_std_devs, key=cycle_std_devs.get)
        min_std_dev = cycle_std_devs[most_consistent_number]

        print(f"Số có chu kỳ đều nhất là {most_consistent_number} với độ lệch chuẩn {min_std_dev:.2f}")
        
        # Dự đoán thời điểm xuất hiện tiếp theo của số có chu kỳ đều nhất
        occurrences = []
        for idx, row in data.iterrows():
            if most_consistent_number in row.values:
                occurrences.append(idx)

        cycles = np.diff(occurrences)
        average_cycle = np.mean(cycles)
        last_occurrence = occurrences[-1]
        predicted_next = last_occurrence + average_cycle

        print(f"Dự đoán số {most_consistent_number} sẽ xuất hiện vào khoảng lượt thứ {predicted_next:.0f} (so với lần cuối cùng xuất hiện).\n")

        # # Vẽ biểu đồ chu kỳ của con số đều nhất
        # plt.figure(figsize=(10, 6))
        # plt.plot(cycles, marker='o', linestyle='-', color='blue', label=f'Chu kỳ của số {most_consistent_number}')
        # plt.axhline(y=average_cycle, color='red', linestyle='--', label='Chu kỳ trung bình')
        # plt.title(f'Chu kỳ xuất hiện đều nhất của số {most_consistent_number}')
        # plt.xlabel('Lần xuất hiện (index)')
        # plt.ylabel('Chu kỳ (số lần giữa các lần xuất hiện)')
        # plt.legend()
        # plt.grid(True)
        # plt.show()

        return most_consistent_number

    def longest_absent_number(self, numbers_to_predict):
        # Đọc dữ liệu từ file CSV không có tiêu đề
        data = pd.read_csv(self.file_path, header=None)  # Thay 'path_to_your_file.csv' bằng đường dẫn đến file của bạn

        last_occurrences = {}

        # Duyệt qua từng số trong danh sách cần dự đoán
        for number_to_predict in numbers_to_predict:
            occurrences = []

            # Duyệt qua các dòng dữ liệu và ghi lại vị trí (index) mà số đó xuất hiện
            for idx, row in data.iterrows():
                if number_to_predict in row.values:
                    occurrences.append(idx)

            if occurrences:
                last_occurrences[number_to_predict] = occurrences[-1]

        # Tìm con số lâu chưa xuất hiện
        max_time_since_last_occurrence = -1
        longest_absent_number = None

        # Xác định thời gian kể từ lần xuất hiện cuối cùng
        for number in numbers_to_predict:
            if number in last_occurrences:
                time_since_last_occurrence = data.shape[0] - last_occurrences[number]  # Số dòng - lần xuất hiện cuối
                if time_since_last_occurrence > max_time_since_last_occurrence:
                    max_time_since_last_occurrence = time_since_last_occurrence
                    longest_absent_number = number

        if longest_absent_number is not None:
            print(f"Số lâu chưa xuất hiện là {longest_absent_number} với thời gian kể từ lần xuất hiện cuối cùng là {max_time_since_last_occurrence} lượt.")
        else:
            print("Không có số nào trong danh sách đã xuất hiện.")

        return longest_absent_number

    def calculate_combined_score(self, numbers_to_predict):
        # Đọc dữ liệu từ file CSV không có tiêu đề
        data = pd.read_csv(self.file_path, header=None)

        last_occurrences = {}
        cycle_std_devs = {}

        for number_to_predict in numbers_to_predict:
            occurrences = []

            # Ghi lại vị trí xuất hiện của các con số
            for idx, row in data.iterrows():
                if number_to_predict in row.values:
                    occurrences.append(idx)

            if occurrences:
                # Ghi lại lần xuất hiện cuối cùng của từng số
                last_occurrences[number_to_predict] = occurrences[-1]
                
                # Tính chu kỳ giữa các lần xuất hiện và độ lệch chuẩn của chu kỳ
                if len(occurrences) > 1:
                    cycles = np.diff(occurrences)
                    std_dev = np.std(cycles)
                    cycle_std_devs[number_to_predict] = std_dev
                else:
                    cycle_std_devs[number_to_predict] = np.inf  # Nếu không đủ dữ liệu chu kỳ

        # Tính khoảng cách kể từ lần xuất hiện cuối cùng và sự đều đặn chu kỳ
        scores = {}
        max_time_since_last_occurrence = data.shape[0]  # Tổng số dòng dữ liệu
        max_cycle_std_dev = max(cycle_std_devs.values()) if cycle_std_devs.values() else 1

        for number in numbers_to_predict:
            if number in last_occurrences:
                # Điểm khoảng cách dựa trên thời gian kể từ lần xuất hiện cuối cùng (lớn hơn là tốt)
                time_since_last_occurrence = max_time_since_last_occurrence - last_occurrences[number]
                normalized_time_score = time_since_last_occurrence / max_time_since_last_occurrence
                
                # Điểm chu kỳ dựa trên độ lệch chuẩn của chu kỳ (nhỏ hơn là tốt)
                std_dev = cycle_std_devs[number]
                normalized_cycle_score = 1 - (std_dev / max_cycle_std_dev)  # Đảo ngược để độ lệch chuẩn thấp có điểm cao hơn
                
                # Tổng hợp hai chỉ số: có thể điều chỉnh trọng số theo mong muốn
                combined_score = (0.5 * normalized_time_score) + (0.5 * normalized_cycle_score)
                scores[number] = combined_score

        # Sắp xếp theo điểm số tổng hợp giảm dần
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        print("Các con số được sắp xếp theo điểm số kết hợp:")
        for number, score in sorted_scores:
            print(f"Số {number}: Điểm tổng hợp {score:.2f}")

        # return the first number in the sorted list
        return sorted_scores[0][0]

# # # Test the DecisionMaker class
# decisionMaker = DecisionMaker('tien-giang')
# decisionMaker.calculate_combined_score([99, 44, 48, 60, 1, 54, 45, 21, 24, 75, 21, 96, 77, 81, 54, 87, 16, 40])
