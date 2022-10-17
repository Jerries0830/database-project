# PJ说明文档

钟尹骏 19302010025

吴可非 19302010012

[TOC]

## 数据库表结构说明

### department

```mysql
create table if not exists department
(
    departmentId int         not null primary key,
    name         varchar(20) not null
);
```

### faculty

```mysql
create table if not exists faculty
(
    facultyId    varchar(11) not null primary key,
    departmentId int         not null,
    name         varchar(10) not null,
    gender       varchar(4)  not null,
    age          int         not null,
    onboardTime  date        not null,
    address      varchar(20) not null,
    phoneNumber  varchar(15) not null,
    email        varchar(30) not null,
    check (gender in ('男', '女')),
    constraint faculty_department_id_fk
        foreign key (departmentId) references department (departmentId)
            on update cascade on delete cascade
);
```

### instructor

```mysql
create table if not exists instructor
(
    facultyId varchar(11) not null,
    teachTime date        not null,
    constraint instructor_id_uindex
        unique (facultyId),
    constraint instructor_faculty_id_fk
        foreign key (facultyId) references faculty (facultyId)
            on update cascade on delete cascade
);
```

### manager

```mysql
create table if not exists manager
(
    facultyId    varchar(11) not null,
    departmentId int         not null,
    constraint manager_departmentId_uindex
        unique (departmentId),
    constraint manager_facultyId_uindex
        unique (facultyId),
    constraint manager_department_id_fk
        foreign key (departmentId) references department (departmentId)
            on update cascade on delete cascade,
    constraint manager_faculty_id_fk
        foreign key (facultyId) references faculty (facultyId)
            on update cascade on delete cascade
);
```

### course

```mysql
create table if not exists course
(
    courseId     int          not null,
    instructorId varchar(11)  not null,
    courseName   varchar(10)  not null,
    type         varchar(5)   not null,
    content      varchar(100) not null,
    primary key (courseId, instructorId),
    constraint course_instructor_instructorId_fk
        foreign key (instructorId) references instructor (facultyId)
            on update cascade on delete cascade
);
```

### section

```mysql
create table if not exists section
(
    courseId     int                  not null,
    sectionId    int                  not null,
    time         date                 not null,
    status       tinyint(1) default 0 not null,
    primary key (courseId, sectionId),
    constraint section_course_courseId_fk
        foreign key (courseId) references course (courseId)
            on update cascade on delete cascade
);
```

### offers

```mysql
create table if not exists offers
(
    departmentId int                  not null,
    courseId     int                  not null,
    compulsory   tinyint(1) default 1 not null,
    primary key (departmentId, courseId),
    constraint offers_course_courseId_fk
        foreign key (courseId) references course (courseId)
            on update cascade on delete cascade,
    constraint offers_department_id_fk
        foreign key (departmentId) references department (departmentId)
            on update cascade on delete cascade
);
```

### takes

```mysql
create table if not exists takes
(
    facultyId varchar(11) not null,
    courseId  int         not null,
    sectionId int         not null,
    score     int         null,
    pass      tinyint(1)  null,
    constraint takes_pk
        unique (facultyId, courseId, sectionId),
    constraint takes_faculty_id_fk
        foreign key (facultyId) references faculty (facultyId)
            on update cascade on delete cascade,
    constraint takes_section_courseId_sectionId_fk
        foreign key (courseId, sectionId) references section (courseId, sectionId)
            on update cascade on delete cascade
);
```

### log

```mysql
create table if not exists log
(
    id     int auto_increment primary key,
    user   varchar(30)  not null,
    action varchar(256) not null,
    date   date         not null
);
```

## 索引定义说明

每张表上均根据主键定义了unique索引

因为实际写的过程中并没有特别频繁根据某些列查询，就没有定义其它索引

## 存储过程说明

同commands文件中功能一样，起到查询或修改的目的，但主要存放一些用python不易实现或理解的操作

### enroll

部门经理为员工安排上课，需要检查是否可以安排、是否已经结课、是否已经通过课程和是否已经在该开课中

```mysql
create
    definer = root@localhost procedure enroll(IN dept_id int, IN course_id int, IN section_id int,
                                              IN faculty_id varchar(11))
begin
    declare required bool;
    set required = (select compulsory from offers where departmentId = dept_id and courseId = course_id);

    if required != 0 or required is null then
        select 1;
    elseif (select status from section where courseId = course_id and sectionId = section_id) = 1 then
        select 2;
    elseif ((select max(pass) from takes where facultyId = faculty_id and courseId = course_id) = 1) then
        select 3;
    elseif (select count(*)
            from takes
            where facultyId = faculty_id and courseId = course_id and sectionId = section_id) then
        select 4;
    else
        insert into takes(facultyId, courseId, sectionId) values (faculty_id, course_id, section_id);
        select 0;
    end if;
end;
```

### get_unfinished_courses

查询员工未上完的课，包含没有通过的课以及正在上的课

```mysql
create
    definer = root@localhost procedure get_unfinished_courses(IN faculty_id varchar(11))
begin
    select distinct courseName, pass
    from (
             select courseId, pass
             from takes
             where facultyId = faculty_id
               and pass is null
             union
             select courseId, max(pass) as passed
             from takes
             where facultyId = faculty_id
             group by courseId
             having passed < 1) as unfinished
             natural join course;
end;
```



## 触发器说明

### faculty

添加员工之后，为员工安排所属部门的必修课

```mysql
create definer = root@localhost trigger faculty_insert_trigger
    after insert
    on faculty
    for each row
begin
    insert into takes(facultyId, courseId, sectionId)
    select NEW.facultyId, courseId, max(sectionId)
    from section
             natural join (select courseId
                           from offers
                           where departmentId = NEW.departmentId
                             and compulsory = true) as compulsory
    where status = false
    group by courseId;
end;
```

更新员工部门之前，检查是否存在未修读完或未通过的课程

```mysql
create definer = root@localhost trigger faculty_before_update_trigger
    before update
    on faculty
    for each row
begin
    declare row_count int;
    declare courses varchar(256);
    if ((OLD.departmentId is null) != (NEW.departmentId is null)) or (OLD.departmentId != NEW.departmentId) then
        set row_count = (select count(*)
                         from (select distinct courseId
                               from takes
                               where facultyId = NEW.facultyId
                               group by courseId
                               having max(pass) != 1

                               union

                               select courseId
                               from takes
                               where facultyId = NEW.facultyId
                                 and pass is null
                              ) as unfinished);
        if row_count > 0 then
            set courses = (select concat('未完成课程：', group_concat(courseName separator ','))
                           from course
                                    join (select distinct courseId
                                          from takes
                                          where facultyId = NEW.facultyId
                                          group by courseId
                                          having max(pass) != 1

                                          union

                                          select courseId
                                          from takes
                                          where facultyId = NEW.facultyId
                                            and pass is null
                           ) as unfinished on course.courseId = unfinished.courseId);
            signal sqlstate 'ERROR'
                set message_text = courses;
        end if;
    end if;
end;
```

更新员工部门之后，为员工安排新部门未通过的必修课

```mysql
create definer = root@localhost trigger faculty_after_update_trigger
    after update
    on faculty
    for each row
begin
    if ((OLD.departmentId is null) != (NEW.departmentId is null)) or (OLD.departmentId != NEW.departmentId) then
        insert into takes(facultyId, courseId, sectionId)
        select NEW.facultyId, courseId, max(sectionId)
        from section
                 natural join (select courseId
                               from offers
                               where departmentId = NEW.departmentId
                                 and compulsory = true
                                 and courseId not in
                                     (select courseId
                                      from takes
                                      where facultyId = NEW.facultyId
                                        and pass is not null
                                        and pass = true)) as compulsory
        where status = false
        group by courseId;
    end if;
end;
```

### takes

添加选课记录之前，检查该课程是否对员工所属部门开放

```mysql
create definer = root@localhost trigger takes_before_insert_trigger
    before insert
    on takes
    for each row
begin
    declare d_id int;
    set d_id = (select departmentId from faculty where faculty.facultyId = NEW.facultyId);

    if (select count(*) from offers where departmentId = d_id and offers.courseId = NEW.courseId) = 0 then
        signal sqlstate 'ERROR' set message_text = '课程不对该员工所属部门开放';
    end if;
end;
```

更新选课成绩之前，检查课程是否结课，未结课时不能修改分数，结课时同步修改课程通过状态

```mysql
create definer = root@localhost trigger takes_before_update_trigger
    before update
    on takes
    for each row
begin
    declare pass_is_changed, score_is_changed bool;
    set score_is_changed = ((OLD.score is null) != (NEW.score is null)) or (OLD.score != NEW.score);
    set pass_is_changed = ((OLD.pass is null) != (NEW.pass is null)) or (OLD.pass != NEW.pass);

    if score_is_changed then
        if (select status from section where courseId = NEW.courseId and sectionId = NEW.sectionId) = false then
            signal sqlstate 'ERROR' set message_text = '未结课，不能修改分数';
        else
            set NEW.pass = (NEW.score >= 60);
        end if;
    end if;
end;
```