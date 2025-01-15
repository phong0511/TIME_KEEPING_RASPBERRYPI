import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js'
import {
  getDatabase,
  ref,
  set,
  push,
  onValue,
  remove,
} from 'https://www.gstatic.com/firebasejs/9.17.1/firebase-database.js'

// Firebase Configuration
const firebaseConfig = {
  apiKey: 'AIzaSyA8y1iepfXtlSURONUiN3YRHjI7IunC1gE',
  authDomain: 'esp32-dht-47e5d.firebaseapp.com',
  databaseURL: 'https://esp32-dht-47e5d-default-rtdb.asia-southeast1.firebasedatabase.app',
  projectId: 'esp32-dht-47e5d',
  storageBucket: 'esp32-dht-47e5d.firebasestorage.app',
  messagingSenderId: '577240316281',
  appId: '1:577240316281:web:2704461c2a866ed71f57a8',
  measurementId: 'G-VKP0QN2QQ2',
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const database = getDatabase(app)

// DOM Elements Testttttt
const video = document.getElementById('video')
// const toggleCameraButton = document.getElementById('toggleCamera')
const employeeList = document.getElementById('employeeList')
const total = document.getElementById('total')
const lateCount = document.getElementById('lateCount')
const registerNewButton = document.getElementById('registerNew')
const exportReportButton = document.getElementById('exportReport')

let stream = null
let isCameraOn = false

// Load employees from Firebase
const employeesRef = ref(database, 'employees')
let employees = []

onValue(employeesRef, (snapshot) => {
  employees = snapshot.val() ? Object.values(snapshot.val()) : []
  renderEmployeeList()
})

function formatTime(date) {
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0') // Đảm bảo 2 chữ số với số 0 đứng đầu
  const minutes = String(date.getMinutes()).padStart(2, '0') // Đảm bảo 2 chữ số với số 0 đứng đầu
  const year = date.getFullYear()
  return {
    day,
    month,
    year,
    fullDay: `${day}/${month}/${year}`,
    formatDay: `${month}/${day}/${year}`, // cần đúng định dạng mm/dd/YYYY
    hours,
    minutes,
    fullTime: `${hours}:${minutes}`,
  }
}

// Display employee list
function renderEmployeeList() {
  employeeList.innerHTML = ''
  let totalCount = employees.length
  let lateCountVal = 0
  console.log(employees)
  employees.forEach((emp) => {
    const regDate = new Date(emp.registerDate)
    const formatRegTime = formatTime(regDate)

    const checkDate = new Date(emp.timeIn)
    const formatCheckTime = formatTime(checkDate)

    let status = 1
    if (formatCheckTime.day > formatRegTime.day) {
      if (Number(formatCheckTime.hours) > 8) status = 0
      else if (Number(formatCheckTime.hours) === 8 && Number(formatCheckTime.minutes) > 0) status = 0
    }
    if (emp.timeIn === 'N/A') status = 2

    if (status === 0) lateCountVal++

    const row = `
      <tr>
        <td>${emp.mssv}</td>
        <td>${emp.name}</td>
        <td>${formatCheckTime.fullDay}</td>
        <td>${formatCheckTime.fullTime}</td>
        <td>${status === 0 ? 'Đi trễ' : status === 2 ? 'Đăng kí mới' : 'Đúng giờ'}</td>
        <td>
          <button class="update-btn" data-index="${emp.mssv}">Cập nhật</button>
          <button class="delete-btn" data-index="${emp.mssv}">Xóa</button>
        </td>
      </tr>`
    employeeList.innerHTML += row
  })

  total.textContent = totalCount
  lateCount.textContent = lateCountVal

  // Add event listeners for update and delete
  document.querySelectorAll('.update-btn').forEach((button) => {
    button.addEventListener('click', handleUpdate)
  })
  document.querySelectorAll('.delete-btn').forEach((button) => {
    button.addEventListener('click', handleDelete)
  })
}

// Toggle Camera
// toggleCameraButton.addEventListener('click', async () => {
//   if (isCameraOn) {
//     stopCamera()
//     toggleCameraButton.textContent = 'Bật Camera'
//   } else {
//     try {
//       stream = await navigator.mediaDevices.getUserMedia({ video: true })
//       video.srcObject = stream
//       isCameraOn = true
//       toggleCameraButton.textContent = 'Tắt Camera'
//     } catch (error) {
//       console.error('Không thể truy cập camera:', error)
//       alert('Kiểm tra quyền truy cập camera!')
//     }
//   }
// })

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop())
    video.srcObject = null
    isCameraOn = false
  }
}

// Register new employee
registerNewButton.addEventListener('click', () => {
  const name = prompt('Nhập tên nhân viên:')
  const mssv = prompt('Nhập MSSV:')
  const date = new Date()
  const registerDate = formatTime(date)
  if (!name) return

  const newEmployee = { mssv, name, timeIn: 'N/A', registerDate: registerDate.formatDay }

  set(ref(database, 'employees/' + mssv), newEmployee)
  alert('Đăng ký thành công!')
})

// Export report
exportReportButton.addEventListener('click', () => {
  const reportData = employees.map((emp) => ({
    Tên: emp.name,
    'Thời Gian': emp.time,
    Buổi: emp.session,
    'Trạng Thái': emp.status,
    'Lịch Hôm Nay': emp.schedule,
  }))

  const ws = XLSX.utils.json_to_sheet(reportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Report')
  XLSX.writeFile(wb, 'Attendance_Report.xlsx')
})

// Update employee
function handleUpdate(event) {
  const index = event.target.dataset.index
  const emp = employees.filter((item) => item.mssv === index)

  const newName = prompt('Nhập tên mới:', emp[0].name)
  const newMSSV = prompt('Nhập mssv mới:', emp[0].mssv)

  if (newName) emp[0].name = newName
  if (newMSSV) emp[0].mssv = newMSSV

  if (!!newMSSV && !!newName) set(ref(database, `employees/${index}`), emp[0])
  alert('Cập nhật thành công!')
}

// Delete employee
function handleDelete(event) {
  const index = event.target.dataset.index
  const confirmDelete = confirm('Bạn có chắc muốn xóa nhân viên này không?')
  if (!confirmDelete) return

  remove(ref(database, `employees/${index}`))
  alert('Xóa thành công!')
}
