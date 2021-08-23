# edx_extended_api

### Learning Tribes extended APIs plugin

### Development
At your devstack, clone the repository to devstack src directory.
Inside lms shell, run
```
pip install -e /edx/src/edx-extended-api
```

### APIs docs

<details>
<summary><b>Create user</b></summary>
<br>

**POST** `/api/users/`

**Body**
```
{
    "username": "user8",
    "email": "user8@example.com",
    "first_name": "first8",
    "last_name": "last8",
    "name": "Eight"
}
```
**Response**
```
{
    "username": "user8",
    "last_name": "last8",
    "lt_exempt_status": true,
    "lt_comments": null,
    "lt_address": null,
    "city": null,
    "first_name": "first8",
    "lt_ilt_supervisor": null,
    "lt_sub_area": null,
    "lt_custom_country": null,
    "location": "",
    "email": "user8@example.com",
    "status": "user_created",
    "bio": null,
    "lt_address_2": null,
    "lt_is_tos_agreed": false,
    "lt_phone_number": null,
    "language": "",
    "year_of_birth": null,
    "lt_area": null,
    "goals": null,
    "lt_employee_id": null,
    "lt_learning_group": null,
    "lt_level": null,
    "lt_hire_date": null,
    "lt_job_code": null,
    "name": "Eight",
    "lt_company": null,
    "lt_supervisor": null,
    "gender": null,
    "lt_gdpr": false,
    "level_of_education": null,
    "country": "",
    "lt_department": null,
    "lt_job_description": null
}
```
</details>



<details>
<summary><b>Get users</b></summary>
<br>

**GET** `/api/users/`

**GET** `/api/users/<user_id>/`

**GET** `/api/users/?user_id=<user_id1,user_id2,…>`

**GET** `/api/users_by_username/<username>/`

**GET** `/api/users_by_username/?username=<username1,username2,…>`

**Response** 
```
{
    "email": "user7@example.com",
    "username": "user7",
    "first_name": "first7",
    "last_name": "last7",
    "language": "",
    "location": "",
    "year_of_birth": null,
    "bio": null,
    "goals": null,
    "level_of_education": null,
    "name": "",
    "gender": null,
    "city": null,
    "country": "",
    "lt_custom_country": null,
    "lt_area": null,
    "lt_sub_area": null,
    "lt_address": null,
    "lt_address_2": null,
    "lt_phone_number": null,
    "lt_gdpr": false,
    "lt_company": null,
    "lt_employee_id": null,
    "lt_hire_date": null,
    "lt_level": null,
    "lt_job_code": null,
    "lt_job_description": null,
    "lt_department": null,
    "lt_supervisor": null,
    "lt_learning_group": null,
    "lt_exempt_status": true,
    "lt_is_tos_agreed": false,
    "lt_comments": null,
    "lt_ilt_supervisor": null,
    "analytics_access": null,
    "internal_catalog_access": false,
    "edflex_catalog_access": false,
    "crehana_catalog_access": false,
    "anderspink_catalog_access": false,
    "learnlight_catalog_access": false,
    "user_id": 30,
    "is_active": true
}
```
```
{
    "count": 2,
    "num_pages": 1,
    "current_page": 1,
    "results": [
        {
            "email": "user6@example.com",
            "username": "user6",
            "first_name": "first6",
            "last_name": "last6",
            "language": "",
            "location": "",
            "year_of_birth": null,
            "bio": null,
            "goals": null,
            "level_of_education": null,
            "name": "",
            "gender": null,
            "city": null,
            "country": "",
            "lt_custom_country": null,
            "lt_area": null,
            "lt_sub_area": null,
            "lt_address": null,
            "lt_address_2": null,
            "lt_phone_number": null,
            "lt_gdpr": false,
            "lt_company": null,
            "lt_employee_id": null,
            "lt_hire_date": null,
            "lt_level": null,
            "lt_job_code": null,
            "lt_job_description": null,
            "lt_department": null,
            "lt_supervisor": null,
            "lt_learning_group": null,
            "lt_exempt_status": true,
            "lt_is_tos_agreed": false,
            "lt_comments": null,
            "lt_ilt_supervisor": null,
            "analytics_access": null,
            "internal_catalog_access": true,
            "edflex_catalog_access": false,
            "crehana_catalog_access": false,
            "anderspink_catalog_access": false,
            "learnlight_catalog_access": false,
            "user_id": 29,
            "is_active": true
        },
        {
            "email": "user7@example.com",
            "username": "user7",
            "first_name": "first7",
            "last_name": "last7",
            "language": "",
            "location": "",
            "year_of_birth": null,
            "bio": null,
            "goals": null,
            "level_of_education": null,
            "name": "",
            "gender": null,
            "city": null,
            "country": "",
            "lt_custom_country": null,
            "lt_area": null,
            "lt_sub_area": null,
            "lt_address": null,
            "lt_address_2": null,
            "lt_phone_number": null,
            "lt_gdpr": false,
            "lt_company": null,
            "lt_employee_id": null,
            "lt_hire_date": null,
            "lt_level": null,
            "lt_job_code": null,
            "lt_job_description": null,
            "lt_department": null,
            "lt_supervisor": null,
            "lt_learning_group": null,
            "lt_exempt_status": true,
            "lt_is_tos_agreed": false,
            "lt_comments": null,
            "lt_ilt_supervisor": null,
            "analytics_access": null,
            "internal_catalog_access": false,
            "edflex_catalog_access": false,
            "crehana_catalog_access": false,
            "anderspink_catalog_access": false,
            "learnlight_catalog_access": false,
            "user_id": 30,
            "is_active": true
        }
    ],
    "next": null,
    "start": 0,
    "previous": null
}
```
</details>
<details>
<summary><b>Update users</b></summary>
<br>

**PUT** `/api/users/<user_id>/`

**PUT** `/api/users_by_username/<username>/`

**Body**

Fields to update
```
{
    "anderspink_catalog_access": true
}
```
**Response**
```
{
    "username": "user7",
    "last_name": "last7",
    "lt_exempt_status": true,
    "lt_comments": null,
    "lt_address": null,
    "city": null,
    "first_name": "first7",
    "lt_ilt_supervisor": null,
    "lt_sub_area": null,
    "edflex_catalog_access": false,
    "lt_custom_country": null,
    "location": "",
    "analytics_access": null,
    "email": "user7@example.com",
    "crehana_catalog_access": false,
    "status": "user_updated",
    "bio": null,
    "lt_address_2": null,
    "lt_is_tos_agreed": false,
    "internal_catalog_access": false,
    "lt_phone_number": null,
    "learnlight_catalog_access": false,
    "language": "",
    "year_of_birth": null,
    "lt_area": null,
    "goals": null,
    "lt_employee_id": null,
    "lt_learning_group": null,
    "lt_level": null,
    "lt_hire_date": null,
    "lt_job_code": null,
    "name": "",
    "lt_company": null,
    "lt_supervisor": null,
    "gender": null,
    "lt_gdpr": false,
    "level_of_education": null,
    "country": "",
    "lt_department": null,
    "anderspink_catalog_access": true,
    "lt_job_description": null
}
```
</details>
<details>
<summary><b>Deactivate user</b></summary>
<br>

**DELETE** `/api/users/<user_id>/`

**DELETE** `/api/users/?user_id=<user_id1,user_id2,…>`

**DELETE** `/api/users_by_username/<username>/`

**DELETE** `/api/users_by_username/?username=<username1,username2,…>`

**Response**
```
{
    "username": "user6",
    "status": "user_deactivated",
    "user_id": 29
}
```
```
[
    {
        "username": "user6",
        "status": "user_deactivated",
        "user_id": 29
    },
    {
        "username": "user7",
        "status": "user_deactivated",
        "user_id": 30
    }
]
```
</details>
<details>
<summary><b>Get courses</b></summary>
<br>

**GET** `/api/courses/`

**Response**
```
{
    "count": 2,
    "num_pages": 1,
    "current_page": 1,
    "results": [
        {
            "id": "course-v1:edX+DemoX+Demo_Course",
            "display_name": "Demonstration Course",
            "overview_url": "http://edx.devstack.lms:18000/courses/course-v1:edX+DemoX+Demo_Course/about",
            "start": "2013-02-05T05:00:00Z",
            "card_image_url": "http://edx.devstack.lms:18000/asset-v1:edX+DemoX+Demo_Course+type@asset+block@images_course_image.jpg",
            "banner_image_url": "http://edx.devstack.lms:18000/static/images/pencils.jpg",
            "short_description": null,
            "instructors": [],
            "effort": null,
            "language": null,
            "course_category": null,
            "tags": [],
            "countries": [],
            "learning_groups": [],
            "modified": "2021-08-10T09:19:05.182673Z"
        },
        {
            "id": "course-v1:edX+E2E-101+course",
            "display_name": "E2E Test Course",
            "overview_url": "http://edx.devstack.lms:18000/courses/course-v1:edX+E2E-101+course/about",
            "start": "2016-01-01T00:00:00Z",
            "card_image_url": "http://edx.devstack.lms:18000/static/images/pencils.jpg",
            "banner_image_url": "http://edx.devstack.lms:18000/static/images/pencils.jpg",
            "short_description": "",
            "instructors": [],
            "effort": null,
            "language": null,
            "course_category": null,
            "tags": [],
            "countries": [],
            "learning_groups": [],
            "modified": "2021-08-10T09:51:01.100924Z"
        }
    ],
    "next": null,
    "start": 0,
    "previous": null
}
```
</details>
<details>
<summary><b>Get user progress report</b></summary>
<br>

**GET** `/api/user_progress_report/<user_id>/`

**GET** `/api/user_progress_report/?user_id=<user_id1,user_id2,…>/`

**GET** `/api/user_progress_report_by_username/<username>/`

**GET** `/api/user_progress_report_by_username/?username=<username1,username2,…>`

**Response**
```
{
    "user_id": 2,
    "username": "edx",
    "name": "",
    "courses": []
}
```
```
{
    "count": 2,
    "num_pages": 1,
    "current_page": 1,
    "results": [
        {
            "user_id": 2,
            "username": "edx",
            "name": "",
            "courses": []
        },
        {
            "user_id": 29,
            "username": "user6",
            "name": "",
            "courses": []
        }
    ],
    "next": null,
    "start": 0,
    "previous": null
}
```
</details>
